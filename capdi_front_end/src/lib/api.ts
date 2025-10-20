// src/lib/api.ts
import { get } from 'svelte/store';
import { authStore, type AuthState } from '$lib/stores/auth';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

// ----------------------
// Helper functions
// ----------------------

// Create headers with optional Authorization
function createHeaders(accessToken: string | null, customHeaders?: HeadersInit): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(customHeaders as Record<string, string>)
  };
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
  return headers;
}

// Core fetch wrapper with automatic refresh
export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const authState: AuthState = get(authStore);
  let accessToken = authState.accessToken;
  let response: Response;

  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: createHeaders(accessToken, options.headers),
      credentials: 'include'
    });

    // Retry once if 401
    if (response.status === 401) {
      const newToken = await authStore.refreshAccessToken();
      if (!newToken) throw new ApiError('Session expired', 401);

      response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: createHeaders(newToken, options.headers),
        credentials: 'include'
      });
    }
  } catch (err) {
    console.error('API request failed:', err);
    throw new ApiError('Network or fetch error');
  }

  return response;
}

// JSON wrapper
export async function apiJson<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(endpoint, options);

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const text = await response.text();
      if (text) message = text;
    } catch {}
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  try {
    return await response.json();
  } catch {
    throw new ApiError('Invalid JSON response');
  }
}

// ----------------------
// API client
// ----------------------
export const apiClient = {
  get: <T = any>(endpoint: string, options?: RequestInit) => apiJson<T>(endpoint, { ...options, method: 'GET' }),
  post: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiJson<T>(endpoint, { ...options, method: 'POST', body: data ? JSON.stringify(data) : undefined }),
  put: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiJson<T>(endpoint, { ...options, method: 'PUT', body: data ? JSON.stringify(data) : undefined }),
  patch: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiJson<T>(endpoint, { ...options, method: 'PATCH', body: data ? JSON.stringify(data) : undefined }),
  delete: <T = any>(endpoint: string, options?: RequestInit) => apiJson<T>(endpoint, { ...options, method: 'DELETE' }),

  // Upload helper (multipart/form-data) with auth
  upload: async (endpoint: string, file: File, options?: RequestInit) => {
    const formData = new FormData();
    formData.append('file', file);

    const authState: AuthState = get(authStore);
    const accessToken = authState.accessToken;

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      body: formData,
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
      credentials: 'include',
      ...options
    });

    if (!response.ok) {
      const text = await response.text();
      throw new ApiError(text || `HTTP ${response.status}`, response.status);
    }

    return await response.json();
  }
};

// ----------------------
// API endpoints
// ----------------------
export const authApi = {
  login: (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    formData.append('grant_type', 'password');
    return apiJson<TokenResponse>('/auth/login', {
      method: 'POST',
      body: formData,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  register: (data: { email: string; password: string; role?: string }) => apiClient.post('/auth/register', data),
  logout: () => apiClient.post('/auth/logout'),
  getMe: () => apiClient.get('/auth/me'),
  refreshToken: () => apiClient.post<TokenResponse>('/auth/refresh'),
  requestPasswordReset: (email: string) => apiClient.post('/auth/reset-password/request', { email }),
  confirmPasswordReset: (token: string, newPassword: string) =>
    apiClient.post('/auth/reset-password/confirm', { token, new_password: newPassword })
};

export const usersApi = {
  list: () => apiClient.get<UserRead[]>('/users/users/'),
  get: (id: number) => apiClient.get<UserRead>(`/users/users/${id}`),
  create: (data: UserCreate) => apiClient.post<UserRead>('/users/users/', data),
  update: (id: number, data: UserUpdate) => apiClient.put<UserRead>(`/users/users/${id}`, data),
  delete: (id: number) => apiClient.delete(`/users/users/${id}`)
};

export const pagesApi = {
  list: () => apiClient.get<PageRead[]>('/pages/pages/'),
  get: (id: number) => apiClient.get<PageRead>(`/pages/pages/${id}`),
  create: (data: PageCreate) => apiClient.post<PageRead>('/pages/pages/', data),
  update: (id: number, data: PageUpdate) => apiClient.put<PageRead>(`/pages/pages/${id}`, data),
  delete: (id: number) => apiClient.delete(`/pages/pages/${id}`)
};

export const mediaApi = {
  list: () => apiClient.get<MediaRead[]>('/media/media/'),
  upload: (file: File) => apiClient.upload('/media/media/', file),
  delete: (id: number) => apiClient.delete(`/media/media/${id}`)
};

export const settingsApi = {
  list: () => apiClient.get<SiteSettingRead[]>('/settings/site-settings/'),
  get: (key: string) => apiClient.get<SiteSettingRead>(`/settings/site-settings/${key}`),
  create: (data: SiteSettingCreate) => apiClient.post<SiteSettingRead>('/settings/site-settings/', data),
  update: (key: string, data: SiteSettingUpdate) => apiClient.put<SiteSettingRead>(`/settings/site-settings/${key}`, data),
  delete: (key: string) => apiClient.delete(`/settings/site-settings/${key}`),

  // ✅ Upsert method
  upsert: (key: string, data: SiteSettingUpdate) =>
    apiClient.post<SiteSettingRead>(`/settings/site-settings/upsert/${key}`, data)
};

export const auditLogsApi = {
  list: () => apiClient.get<AuditLogRead[]>('/audit-logs/audit-logs/')
};

// ----------------------
// Type definitions
// ----------------------
interface UserRead { email: string; role: string; is_active: boolean; id: number; created_at: string; updated_at: string; }
interface UserCreate { email: string; password: string; role?: string | null; }
interface UserUpdate { email?: string | null; role?: string | null; is_active?: boolean | null; password?: string | null; }
interface PageRead { slug: string; title: string; is_published: boolean; id: number; created_at: string; updated_at: string; }
interface PageCreate { slug: string; title: string; is_published?: boolean; }
interface PageUpdate { title?: string | null; slug?: string | null; is_published?: boolean | null; }
interface MediaRead { filename: string; filepath: string; mimetype: string; id: number; uploaded_by_id: number; uploaded_at: string; }
interface SiteSettingRead { value: string; id: number; key: string; updated_at: string; }
interface SiteSettingCreate { value: string; key: string; }
interface SiteSettingUpdate { value: string; }
interface AuditLogRead { action: string; resource_type: string; resource_id: number; id: number; user_id: number; timestamp: string; }
