<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { usersApi, pagesApi, mediaApi, auditLogsApi } from '$lib/api';

	type DashboardStats = {
		users: number;
		pages: number;
		media: number;
		visits: number;
	};

	let stats: DashboardStats = { users: 0, pages: 0, media: 0, visits: 0 };
	let recentActivity: { message: string; time: string }[] = [];
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			const [users, pages, media, logs] = await Promise.all([
				usersApi.list(),
				pagesApi.list(),
				mediaApi.list(),
				auditLogsApi.list()
			]);

			stats = {
				users: users.length,
				pages: pages.length,
				media: media.length,
				visits: 5821 // Placeholder — replace later with analytics endpoint
			};

			recentActivity = logs
				.slice(0, 5)
				.map((log) => ({
					message: `${log.action} ${log.resource_type} #${log.resource_id}`,
					time: new Date(log.timestamp).toLocaleString()
				}));
		} catch (err) {
			console.error(err);
			error = 'Failed to load dashboard data.';
		} finally {
			loading = false;
		}
	});

	function goTo(path: string) {
		goto(path);
	}
</script>

<main class="space-y-6 animate-fade-in">
	<!-- Page Header -->
	<div class="flex justify-between items-center flex-wrap gap-3">
		<h1 class="text-2xl sm:text-3xl font-bold text-gray-800">Dashboard Overview</h1>
		<button
			class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm text-sm sm:text-base transition"
			on:click={() => goTo('/admin/settings')}
		>
			Manage Settings
		</button>
	</div>

	{#if loading}
		<div class="flex justify-center items-center py-16 text-gray-400">Loading dashboard...</div>
	{:else if error}
		<div class="p-6 bg-red-50 text-red-600 rounded-lg">{error}</div>
	{:else}
		<!-- Stats Grid -->
		<section class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
			{#each [
				{ label: 'Users', value: stats.users, color: 'from-blue-500 to-blue-600', icon: '👥' },
				{ label: 'Pages', value: stats.pages, color: 'from-green-500 to-green-600', icon: '📄' },
				{ label: 'Media', value: stats.media, color: 'from-purple-500 to-purple-600', icon: '🖼️' },
				{ label: 'Visits', value: stats.visits, color: 'from-orange-500 to-orange-600', icon: '📊' }
			] as card}
				<div
					class="bg-white shadow-sm rounded-xl border border-gray-100 p-5 hover:shadow-md transition-transform hover:-translate-y-1 cursor-pointer"
				>
					<div class="flex items-center justify-between mb-2">
						<div class="text-2xl">{card.icon}</div>
						<div
							class={`w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center text-white text-lg font-semibold`}
						>
							{card.value > 99 ? '+' : ''}
						</div>
					</div>
					<p class="text-gray-500 text-sm uppercase tracking-wide">{card.label}</p>
					<p class="text-2xl font-bold text-gray-800 mt-1">{card.value}</p>
				</div>
			{/each}
		</section>

		<!-- Activity and Chart -->
		<section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Chart Placeholder -->
			<div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
				<h2 class="text-lg font-semibold text-gray-700 mb-4">Traffic Overview</h2>
				<div
					class="w-full h-64 flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-lg"
				>
					📈 Chart Placeholder (integrate analytics or Recharts later)
				</div>
			</div>

			<!-- Recent Activity -->
			<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
				<h2 class="text-lg font-semibold text-gray-700 mb-4">Recent Activity</h2>

				{#if recentActivity.length > 0}
					<ul class="space-y-3">
						{#each recentActivity as item}
							<li class="flex justify-between items-start bg-gray-50 hover:bg-gray-100 rounded-lg px-3 py-2 transition">
								<p class="text-sm text-gray-700">{item.message}</p>
								<span class="text-xs text-gray-500">{item.time}</span>
							</li>
						{/each}
					</ul>
				{:else}
					<p class="text-gray-400 text-sm">No recent activity.</p>
				{/if}
			</div>
		</section>
	{/if}
</main>

<style>
	@keyframes fade-in {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	.animate-fade-in {
		animation: fade-in 0.4s ease-out;
	}
</style>
