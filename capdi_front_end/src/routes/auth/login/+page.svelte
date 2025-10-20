<script lang="ts">
	import { authApi } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let email = '';
	let password = '';
	let errorMessage = '';
	let loading = false;

	async function handleLogin(event: Event) {
		event.preventDefault();
		errorMessage = '';
		loading = true;

		try {
			const tokenData = await authApi.login(email, password);

			// Save tokens to store
			authStore.setTokens(tokenData.access_token);

			// Optionally fetch user profile
			const user = await authApi.getMe();
			if ('setUser' in authStore && typeof authStore.setUser === 'function') {
				authStore.setUser(user);
			}

			// Redirect to dashboard
			goto('/admin/dashboard');
		} catch (err: any) {
			console.error('Login failed:', err);
			errorMessage = 'Invalid email or password. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<main class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 text-gray-800 px-4">
	<section class="w-full max-w-md bg-white shadow-lg rounded-2xl p-8 border border-gray-100">
		<!-- Breadcrumbs -->
		<nav class="text-sm mb-6 text-gray-500">
			<a href="/" class="hover:text-blue-600">Home</a>
			<span class="mx-2">›</span>
			<span class="text-gray-700 font-medium">Login</span>
		</nav>

		<h1 class="text-3xl sm:text-4xl font-extrabold text-blue-700 text-center mb-6">
			CARING FOR PEOPLE WITH DISABILITIES
		</h1>

		<form on:submit|preventDefault={handleLogin} class="space-y-5">
			<div>
				<label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
				<input
					bind:value={email}
					type="email"
					id="email"
					required
					placeholder="you@example.com"
					class="form-input w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-100 transition"
				/>
			</div>

			<div>
				<label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
				<input
					bind:value={password}
					type="password"
					id="password"
					required
					placeholder="••••••••"
					class="form-input w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-100 transition"
				/>
			</div>

			{#if errorMessage}
				<p class="text-red-600 text-sm text-center">{errorMessage}</p>
			{/if}

			<button
				type="submit"
				class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg shadow-md transition disabled:opacity-50"
				disabled={loading}
			>
				{#if loading}
					<span class="animate-pulse">Signing in...</span>
				{:else}
					Sign In
				{/if}
			</button>
		</form>

		<p class="text-center text-sm text-gray-500 mt-6">
			Don’t have an account?
			<a href="/auth/register" class="text-blue-600 hover:text-blue-700 font-medium">
				Register
			</a>
		</p>
	</section>
</main>
