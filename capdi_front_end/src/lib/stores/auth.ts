// src/lib/stores/auth.ts
import { writable } from 'svelte/store';
import { apiJson } from '$lib/api';

interface AuthState {
	user: any | null;
	accessToken: string | null;
	refreshToken: string | null;
	loading: boolean;
}

function createAuthStore() {
	const stored = localStorage.getItem('auth');
	const initial: AuthState = stored
		? JSON.parse(stored)
		: { user: null, accessToken: null, refreshToken: null, loading: false };

	const { subscribe, set, update } = writable(initial);

	function persist(state: AuthState) {
		localStorage.setItem('auth', JSON.stringify(state));
	}

	async function login(email: string, password: string) {
		update((s) => ({ ...s, loading: true }));
		const data = await apiJson('/auth/login', {
			method: 'POST',
			body: JSON.stringify({ email, password })
		});

		const user = await apiJson('/auth/me', {
			headers: { Authorization: `Bearer ${data.access_token}` }
		});

		const newState = {
			user,
			accessToken: data.access_token,
			refreshToken: data.refresh_token,
			loading: false
		};
		set(newState);
		persist(newState);
	}

	function logout() {
		set({ user: null, accessToken: null, refreshToken: null, loading: false });
		localStorage.removeItem('auth');
	}

	function setTokens(access: string, refresh: string) {
		update((s) => {
			const newState = { ...s, accessToken: access, refreshToken: refresh };
			persist(newState);
			return newState;
		});
	}

	return {
		subscribe,
		login,
		logout,
		setTokens
	};
}

export const authStore = createAuthStore();
