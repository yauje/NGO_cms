// src/routes/+layout.ts
import type { LayoutLoad } from './$types';
import { authStore } from '$lib/stores/auth';
import { get } from 'svelte/store';

export const load: LayoutLoad = async () => {
	// just provide user info if logged in
	const { user } = get(authStore);

	return { user };
};
