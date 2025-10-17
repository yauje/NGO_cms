// src/routes/+layout.ts
import type { LayoutLoad } from './$types';
import { authStore } from '$lib/stores/auth';
import { get } from 'svelte/store';
import { redirect } from '@sveltejs/kit';

export const load: LayoutLoad = async () => {
	const { user, accessToken } = get(authStore);

	if (!accessToken) {
		throw redirect(302, '/(auth)/login');
	}

	return { user };
};
