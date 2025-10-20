<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { settingsApi, mediaApi } from '$lib/api';

	type SettingRead = { key: string; value: string; description?: string; id?: number };
	type Tab = 'site' | 'theme' | 'social' | 'contact';

	// Tabs + field metadata (includes select options for theme)
	const tabs: { key: Tab; label: string }[] = [
		{ key: 'site', label: 'Site Info' },
		{ key: 'theme', label: 'Theme' },
		{ key: 'social', label: 'Social Links' },
		{ key: 'contact', label: 'Contact' }
	];

	const fontOptions = ['Inter', 'Roboto', 'Open Sans', 'Poppins', 'Lato', 'Montserrat'];
	const radiusOptions = ['0px', '4px', '8px', '12px', '16px'];
	const shadowOptions = ['none', 'sm', 'md', 'lg'];

	const fields: Record<
		Tab,
		{ key: string; label: string; type?: 'text' | 'textarea' | 'color' | 'media' | 'select' }[]
	> = {
		site: [
			{ key: 'site.title', label: 'Site Title', type: 'text' },
			{ key: 'site.tagline', label: 'Tagline', type: 'textarea' },
			{ key: 'site.logo', label: 'Logo', type: 'media' },
			{ key: 'site.favicon', label: 'Favicon', type: 'media' },
			{ key: 'site.hero_image', label: 'Hero Image', type: 'media' }
		],
		theme: [
			{ key: 'theme.primary_color', label: 'Primary Color', type: 'color' },
			{ key: 'theme.secondary_color', label: 'Secondary Color', type: 'color' },
			{ key: 'theme.background_color', label: 'Background Color', type: 'color' },
			{ key: 'theme.text_color', label: 'Text Color', type: 'color' },
			{ key: 'theme.accent_color', label: 'Accent Color', type: 'color' },
			{ key: 'theme.font_family', label: 'Font Family', type: 'select' },
			{ key: 'theme.border_radius', label: 'Corner Radius', type: 'select' },
			{ key: 'theme.shadow_depth', label: 'Shadow Depth', type: 'select' }
		],
		social: [
			{ key: 'social.facebook', label: 'Facebook URL', type: 'text' },
			{ key: 'social.twitter', label: 'Twitter URL', type: 'text' },
			{ key: 'social.instagram', label: 'Instagram URL', type: 'text' }
		],
		contact: [
			{ key: 'contact.email', label: 'Email', type: 'text' },
			{ key: 'contact.phone', label: 'Phone', type: 'text' },
			{ key: 'contact.address', label: 'Address', type: 'textarea' }
		]
	};

	let activeTab: Tab = 'site';

	// settings map and snapshots
	let settings: Record<string, string> = {};
	let originalSettings: Record<string, string> = {};

	// per-field statuses
	let saving: Record<string, boolean> = {};
	let saveSuccess: Record<string, boolean> = {};
	let uploading: Record<string, boolean> = {};

	let loading = false;
	let error: string | null = null;
	let success: string | null = null;

	// helper: get flattened list of all keys we care about (from fields definition)
	const allFieldKeys = Object.values(fields).flat().map((f) => f.key);

	onMount(loadSettings);

	async function loadSettings() {
		loading = true;
		error = null;
		try {
			const data: SettingRead[] = await settingsApi.list();
			// populate defaults: ensure keys exist so bindings don't break
			allFieldKeys.forEach((k) => {
				settings[k] = '';
			});
			// apply returned settings into our map
			data.forEach((s) => {
				settings[s.key] = s.value ?? '';
			});
			// snapshot for change detection
			originalSettings = { ...settings };
		} catch (err) {
			console.error(err);
			error = 'Failed to load site settings.';
		} finally {
			loading = false;
		}
	}

	// computed: whether a particular field has unsaved changes
	function isChanged(key: string) {
		return (originalSettings[key] ?? '') !== (settings[key] ?? '');
	}

	// computed: overall unsaved changes flag
	function hasUnsavedChanges() {
		return Object.keys(settings).some((k) => isChanged(k));
	}

	// Save single setting (uses upsert endpoint)
	async function saveSetting(key: string) {
		// basic validation: don't save empty strings for non-media fields
		const meta = findFieldMeta(key);
		if (!meta) return;
		if (meta.type !== 'media' && !(settings[key] ?? '').toString().trim()) {
			error = 'Value required before saving.';
			return;
		}
		// For media fields ensure URL exists (upload must happen first)
		if (meta.type === 'media' && !(settings[key] ?? '').toString().trim()) {
			error = 'Please upload a file first.';
			return;
		}

		error = null;
		saveSuccess[key] = false;
		saving[key] = true;
		try {
			await settingsApi.upsert(key, { value: settings[key] ?? '' });
			// Update snapshot so this field is considered saved
			originalSettings[key] = settings[key] ?? '';
			saveSuccess[key] = true;
			// Auto-hide per-field success after short time
			setTimeout(() => (saveSuccess[key] = false), 2500);
		} catch (err) {
			console.error('saveSetting error', err);
			error = `Failed to save ${key}.`;
		} finally {
			saving[key] = false;
		}
	}

	// Apply all changed settings in batch (only apply keys that changed)
	async function applyAllChanges() {
		if (!hasUnsavedChanges()) {
			success = 'No changes to apply.';
			setTimeout(() => (success = null), 2000);
			return;
		}
		error = null;
		success = null;
		loading = true;
		try {
			// collect changed keys only
			const changedKeys = Object.keys(settings).filter((k) => isChanged(k));
			// sequentially upsert to give clear logging and avoid spamming backend
			for (const key of changedKeys) {
				await settingsApi.upsert(key, { value: settings[key] ?? '' });
				originalSettings[key] = settings[key] ?? '';
			}
			success = '✅ All changes applied successfully!';
			setTimeout(() => (success = null), 3000);
		} catch (err) {
			console.error('applyAllChanges error', err);
			error = '❌ Failed to apply settings.';
		} finally {
			loading = false;
		}
	}

	// Upload media then set the setting value to returned file URL.
	// mediaApi.upload returns a Response object; parse JSON safely.
	async function handleFileChange(key: string, file: File | null) {
		if (!file) return;
		uploading[key] = true;
		error = null;
		try {
			const resp = await mediaApi.upload(file);
			// The upload endpoint returns JSON of uploaded media (MediaRead).
			// If apiClient.upload returns a Response, parse it; if it already returned parsed,
			// we protectively handle both cases.
			let data: any;
			if (resp instanceof Response) {
				if (!resp.ok) {
					const text = await resp.text();
					throw new Error(`Upload failed: ${resp.status} ${text}`);
				}
				data = await resp.json();
			} else {
				// fallback if upload returned parsed object
				data = resp;
			}

			// Expect `url` field on returned media object
			if (!data || !data.url) {
				throw new Error('Upload returned no URL.');
			}
			settings[key] = data.url;
			// do NOT automatically save — let admin decide to Save or Apply All
		} catch (err) {
			console.error('handleFileChange upload error', err);
			error = `Failed to upload file for ${key}.`;
		} finally {
			uploading[key] = false;
		}
	}

	function findFieldMeta(key: string) {
		for (const tab of Object.keys(fields) as Tab[]) {
			const meta = fields[tab].find((f) => f.key === key);
			if (meta) return meta;
		}
		return null;
	}

	function goBack() {
		goto('/admin/dashboard');
	}

	// Theme preview style derived from settings
	function previewStyles(): string {
		const primary = settings['theme.primary_color'] || '#2563eb';
		const secondary = settings['theme.secondary_color'] || '#10b981';
		const bg = settings['theme.background_color'] || '#ffffff';
		const text = settings['theme.text_color'] || '#111827';
		const accent = settings['theme.accent_color'] || primary;
		const font = settings['theme.font_family'] || 'Inter';
		const radius = settings['theme.border_radius'] || '8px';
		const shadow = settings['theme.shadow_depth'] || 'sm';

		const shadowMap: Record<string, string> = {
			none: 'none',
			sm: '0 1px 3px rgba(0,0,0,0.08)',
			md: '0 4px 8px rgba(0,0,0,0.12)',
			lg: '0 10px 20px rgba(0,0,0,0.16)'
		};

		const styleObj: Record<string, string> = {
			'--preview-primary': primary,
			'--preview-secondary': secondary,
			'--preview-bg': bg,
			'--preview-text': text,
			'--preview-accent': accent,
			'--preview-font': font,
			'--preview-radius': radius,
			'--preview-shadow': shadowMap[shadow] ?? shadowMap.sm
		};

		// Quote font family if it contains spaces
		if (/\s/.test(styleObj['--preview-font'])) {
			styleObj['--preview-font'] = `"${styleObj['--preview-font']}"`;
		}

		return Object.entries(styleObj).map(([k, v]) => `${k}: ${v}`).join('; ');
	}
</script>

<main class="p-6 space-y-6">
	<header class="flex items-start justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Site Settings</h1>
			<p class="text-sm text-gray-500 mt-1">Configure site info, theme, social links and contact details.</p>
		</div>
		<div class="flex items-center gap-2">
			<button class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded" on:click={goBack}>← Dashboard</button>
			<button
				class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-60"
				on:click={applyAllChanges}
				disabled={loading || !hasUnsavedChanges()}
			>
				{loading ? 'Applying...' : 'Apply All Changes'}
			</button>
		</div>
	</header>

	{#if error}
		<div class="p-3 bg-red-50 text-red-700 rounded">{error}</div>
	{/if}
	{#if success}
		<div class="p-3 bg-green-50 text-green-700 rounded">{success}</div>
	{/if}

	<!-- Tabs -->
	<div class="flex gap-2 border-b pb-3">
		{#each tabs as t}
			<button
				on:click={() => (activeTab = t.key)}
				class="px-4 py-2 -mb-px border-b-2 font-medium transition"
				class:bg-white={activeTab === t.key}
				class:border-blue-600={activeTab === t.key}
				class:text-blue-600={activeTab === t.key}
				class:text-gray-500={activeTab !== t.key}
			>
				{t.label}
			</button>
		{/each}
	</div>

	{#if loading}
		<div class="py-10 text-gray-400">Loading settings...</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Form area -->
			<div class="lg:col-span-2 space-y-4">
				{#each fields[activeTab] as field}
					<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
						<div class="flex items-start justify-between">
							<div>
								<!-- svelte-ignore a11y_label_has_associated_control -->
								<label class="block text-sm font-semibold text-gray-800">{field.label}</label>
								<p class="text-xs text-gray-500 mt-1"><!-- you can add descriptions in schema --></p>
							</div>
							<div class="text-right">
								{#if isChanged(field.key)}
									<span class="text-xs text-amber-600">Unsaved</span>
								{/if}
							</div>
						</div>

						<div class="mt-3">
							{#if field.type === 'textarea'}
								<textarea rows="3" bind:value={settings[field.key]} class="w-full rounded border p-2 text-sm"></textarea>
							{:else if field.type === 'color'}
								<div class="flex items-center gap-3">
									<input type="color" bind:value={settings[field.key]} class="w-14 h-10 rounded border" />
									<input type="text" bind:value={settings[field.key]} placeholder="#rrggbb" class="border rounded p-2 text-sm flex-1" />
								</div>
							{:else if field.type === 'media'}
								<div class="flex items-center gap-3">
									<input
										type="file"
										accept="image/*"
										on:change={(e: Event) => handleFileChange(field.key, (e.currentTarget as HTMLInputElement).files?.[0] ?? null)}
									/>
									{#if uploading[field.key]}
										<span class="text-gray-500 text-sm">Uploading...</span>
									{:else if settings[field.key]}
										<img src={settings[field.key]} alt={field.label} class="h-14 w-14 object-contain border rounded" />
									{:else}
										<span class="text-sm text-gray-400">No file uploaded</span>
									{/if}
								</div>
							{:else if field.type === 'select' && field.key === 'theme.font_family'}
								<select bind:value={settings[field.key]} class="border rounded p-2 text-sm w-full mt-2">
									<option value="">(default)</option>
									{#each fontOptions as f}
										<option value={f}>{f}</option>
									{/each}
								</select>
							{:else if field.type === 'select' && field.key === 'theme.border_radius'}
								<select bind:value={settings[field.key]} class="border rounded p-2 text-sm w-full mt-2">
									<option value="">(default)</option>
									{#each radiusOptions as r}
										<option value={r}>{r}</option>
									{/each}
								</select>
							{:else if field.type === 'select' && field.key === 'theme.shadow_depth'}
								<select bind:value={settings[field.key]} class="border rounded p-2 text-sm w-full mt-2">
									<option value="">(default)</option>
									{#each shadowOptions as s}
										<option value={s}>{s}</option>
									{/each}
								</select>
							{:else}
								<input type="text" bind:value={settings[field.key]} class="border rounded p-2 text-sm w-full" />
							{/if}
						</div>

						<div class="mt-3 flex items-center justify-end gap-3">
							<button
								class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
								on:click={() => {
									// revert field to original
									settings[field.key] = originalSettings[field.key] ?? '';
								}}
								disabled={!isChanged(field.key)}
							>
								Revert
							</button>

							<button
								class="px-3 py-1 bg-blue-600 text-white rounded text-sm disabled:opacity-60 flex items-center gap-2"
								on:click={() => saveSetting(field.key)}
								disabled={
									saving[field.key] ||
									(uploading[field.key] ?? false) ||
									(!isChanged(field.key) || (field.type !== 'media' && !(settings[field.key] ?? '').toString().trim()))
								}
							>
								{#if saving[field.key]}Saving...{:else}💾 Save{/if}
							</button>

							{#if saveSuccess[field.key]}
								<span class="text-sm text-green-600">Saved</span>
							{/if}
						</div>
					</div>
				{/each}
			</div>

			<!-- Preview / Utilities -->
			<div class="space-y-4">
				<!-- Theme Preview -->
				<div class="bg-white p-4 rounded-lg border border-gray-100">
					<h3 class="text-sm font-semibold mb-3">Live Theme Preview</h3>
					<div class="p-4 rounded" style={previewStyles()}>
						<div
							style="background: var(--preview-bg); color: var(--preview-text); font-family: var(--preview-font); border-radius: var(--preview-radius); box-shadow: var(--preview-shadow); padding: 16px;"
						>
							<h2 style="color: var(--preview-primary); margin:0;">Example Title</h2>
							<p style="margin:6px 0 12px;">This is a sample paragraph to preview font, text color and spacing.</p>

							<div class="flex gap-2">
								<button style="background: var(--preview-primary); color: white; padding:6px 10px; border-radius:6px;">Primary</button>
								<button style="background: var(--preview-secondary); color: white; padding:6px 10px; border-radius:6px;">Secondary</button>
								<button style="background: var(--preview-accent); color: white; padding:6px 10px; border-radius:6px;">Accent</button>
							</div>
						</div>
					</div>
					<p class="text-xs text-gray-500 mt-2">Choose colors, font and small UI tokens. Click Save per-field or Apply All.</p>
				</div>

				<!-- Unsaved changes indicator -->
				<div class="bg-white p-3 rounded border border-gray-100">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium">Status</p>
							<p class="text-xs text-gray-500">
								{#if hasUnsavedChanges()}
									<span class="text-amber-600">You have unsaved changes</span>
								{:else}
									<span class="text-green-600">All changes saved</span>
								{/if}
							</p>
						</div>
						<div>
							<button
								class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 text-sm"
								on:click={loadSettings}
							>
								Reload
							</button>
						</div>
					</div>
				</div>

				<!-- Quick actions -->
				<div class="bg-white p-3 rounded border border-gray-100">
					<p class="text-sm font-medium mb-2">Quick actions</p>
					<button
						class="w-full px-3 py-2 bg-blue-600 text-white rounded mb-2 hover:bg-blue-700 text-sm"
						on:click={() => {
							// navigate to media manager or create new setting
							goto('/admin/settings/new');
						}}
					>
						+ New Setting
					</button>
				</div>
			</div>
		</div>
	{/if}
</main>

<style>
	:global(body) {
		/* allow preview font to display if available on system; admin can add webfonts later */
		font-family: var(--preview-font, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial);
	}
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
</style>
