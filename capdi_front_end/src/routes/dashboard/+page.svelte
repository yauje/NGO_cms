<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { get } from 'svelte/store';
	const { user } = get(authStore);
</script>

<main class="p-8">
	<h1 class="text-3xl font-bold">Welcome {user?.email}</h1>
	<p class="text-gray-600 mt-2">This is a protected route.</p>
</main>
