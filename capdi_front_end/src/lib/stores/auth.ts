import { writable } from 'svelte/store';
import { apiJson } from '$lib/api';

export interface User {
	id: number;
	email: string;
	role: string;
	is_active: boolean;
	permissions?: Record<string, any>;
	created_at: string;
	updated_at: string;
}

export interface AuthState {
	user: User | null;
	accessToken: string | null;
	refreshToken: string | null; // optional, backend stores in cookie
	loading: boolean;
}

function createAuthStore() {
	// Only access localStorage in the browser
	const stored =
		typeof localStorage !== 'undefined' ? localStorage.getItem('auth') : null;

	const initial: AuthState = stored
		? JSON.parse(stored)
		: { user: null, accessToken: null, refreshToken: null, loading: false };

	const { subscribe, set, update } = writable<AuthState>(initial);

	function persist(state: AuthState) {
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('auth', JSON.stringify(state));
		}
	}

	async function login(email: string, password: string) {
		update((s) => ({ ...s, loading: true }));

		try {
			// Step 1: Login — backend returns access token, sets refresh cookie
			const tokenData = await apiJson<{ access_token: string; token_type: string }>('/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
				body: new URLSearchParams({
					username: email,
					password,
					grant_type: 'password'
				})
			});

			// Step 2: Fetch user details with access token
			const user = await apiJson<User>('/auth/me', {
				headers: { Authorization: `Bearer ${tokenData.access_token}` }
			});

			const newState: AuthState = {
				user,
				accessToken: tokenData.access_token,
				refreshToken: null, // handled via HttpOnly cookie
				loading: false
			};

			set(newState);
			persist(newState);
		} catch (error) {
			console.error('Login failed:', error);
			set({ user: null, accessToken: null, refreshToken: null, loading: false });
			if (typeof localStorage !== 'undefined') localStorage.removeItem('auth');
			throw error;
		}
	}

	function logout() {
		set({ user: null, accessToken: null, refreshToken: null, loading: false });
		if (typeof localStorage !== 'undefined') localStorage.removeItem('auth');
		// Call logout API to clear cookie
		apiJson('/auth/logout', { method: 'POST' }).catch(console.error);
	}

	function setTokens(access: string, refresh?: string) {
		update((state) => {
			const newState = { ...state, accessToken: access, refreshToken: refresh ?? state.refreshToken };
			persist(newState);
			return newState;
		});
	}

	async function refreshAccessToken() {
		try {
			const tokenData = await apiJson<{ access_token: string; token_type: string }>('/auth/refresh', {
				method: 'POST',
				credentials: 'include' // send refresh cookie
			});
			setTokens(tokenData.access_token);
			return tokenData.access_token;
		} catch (err) {
			console.warn('Failed to refresh token:', err);
			logout();
			return null;
		}
	}

	return {
		subscribe,
		login,
		logout,
		setTokens,
		refreshAccessToken
	};
}

export const authStore = createAuthStore();
