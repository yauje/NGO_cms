// src/lib/api.ts
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function apiFetch(
	endpoint: string,
	options: RequestInit = {}
): Promise<Response> {
	const { accessToken, refreshToken, setTokens, logout } = get(authStore);

	const headers: HeadersInit = {
		'Content-Type': 'application/json',
		...(options.headers || {})
	};

	if (accessToken) {
		headers['Authorization'] = `Bearer ${accessToken}`;
	}

	let response = await fetch(`${API_BASE}${endpoint}`, {
		...options,
		headers
	});

	// Handle expired access token
	if (response.status === 401 && refreshToken) {
		const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ refresh_token: refreshToken })
		});

		if (refreshRes.ok) {
			const data = await refreshRes.json();
			setTokens(data.access_token, data.refresh_token);

			// retry original request
			const retryHeaders = {
				...headers,
				Authorization: `Bearer ${data.access_token}`
			};
			response = await fetch(`${API_BASE}${endpoint}`, {
				...options,
				headers: retryHeaders
			});
		} else {
			logout();
			throw new Error('Session expired');
		}
	}

	return response;
}

export async function apiJson<T = any>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const res = await apiFetch(endpoint, options);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}
