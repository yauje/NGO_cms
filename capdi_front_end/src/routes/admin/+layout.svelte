<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let sidebarOpen = false;
	let isMobile = false;

	function navigate(path: string) {
		goto(path);
		if (isMobile) sidebarOpen = false;
	}

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	function handleResize() {
		isMobile = window.innerWidth < 768;
		sidebarOpen = !isMobile;
	}

	onMount(() => {
		handleResize();
		window.addEventListener('resize', handleResize);
		return () => window.removeEventListener('resize', handleResize);
	});

	const navLinks = [
		{ name: 'Dashboard', path: '/admin/dashboard', icon: '🏠' },
		{ name: 'Users', path: '/admin/users', icon: '👥' },
		{ name: 'Pages', path: '/admin/pages', icon: '📄' },
		{ name: 'Media', path: '/admin/media', icon: '🖼️' },
		{ name: 'Settings', path: '/admin/settings', icon: '⚙️' }
	];
</script>

<div class="flex h-screen bg-gray-50 overflow-hidden">
	<!-- Sidebar -->
	<aside
		class="fixed inset-y-0 left-0 bg-white/90 backdrop-blur-md border-r border-gray-200 w-64 flex flex-col z-50
			transform transition-transform duration-300 ease-in-out
			{sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
			md:translate-x-0 md:static"
	>
		<!-- Header -->
		<div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
			<h2 class="text-xl font-bold text-blue-700">Admin</h2>
			<!-- svelte-ignore a11y_consider_explicit_label -->
			<button class="md:hidden p-2 rounded-lg hover:bg-gray-100" on:click={toggleSidebar}>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Navigation -->
		<nav class="flex flex-col flex-1 overflow-y-auto px-3 py-4 space-y-1">
			{#each navLinks as link}
				<button
					class="flex items-center space-x-3 w-full text-left px-4 py-2.5 rounded-lg transition-all duration-200
						text-gray-700 hover:bg-blue-50 hover:text-blue-700"
					on:click={() => navigate(link.path)}
				>
					<span class="text-lg">{link.icon}</span>
					<span class="font-medium">{link.name}</span>
				</button>
			{/each}
		</nav>

		<!-- Footer -->
		<div class="border-t border-gray-100 p-4 text-xs text-gray-500 flex justify-between">
			<span>Version 2.0.1</span>
			<span class="text-blue-600 font-semibold">NextGen UI</span>
		</div>
	</aside>

	<!-- Overlay for mobile -->
	{#if sidebarOpen && isMobile}
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="fixed inset-0 bg-black/40 z-40 md:hidden transition-opacity"
			on:click={toggleSidebar}
		></div>
	{/if}

	<!-- Main Content -->
	<div class="flex-1 flex flex-col min-w-0">
		<header class="flex justify-between items-center bg-white shadow-sm px-4 sm:px-6 py-4 sticky top-0 z-30">
			<div class="flex items-center space-x-3">
				<button
					class="p-2 rounded-lg hover:bg-gray-100 md:hidden"
					on:click={toggleSidebar}
					aria-label="Toggle sidebar"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<h1 class="text-lg sm:text-xl font-semibold text-gray-800 truncate">Admin Console</h1>
			</div>
			<button
				class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center space-x-2 text-sm sm:text-base"
				on:click={() => navigate('/')}
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3..." />
				</svg>
				<span>Logout</span>
			</button>
		</header>

		<main class="flex-1 overflow-auto p-4 sm:p-6 bg-gray-50">
			<slot />
		</main>
	</div>
</div>

<style>
	main {
		scroll-behavior: smooth;
	}
	button:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}
	aside::-webkit-scrollbar {
		width: 6px;
	}
	aside::-webkit-scrollbar-thumb {
		background: #cbd5e1;
		border-radius: 3px;
	}
	aside::-webkit-scrollbar-thumb:hover {
		background: #94a3b8;
	}
</style>
