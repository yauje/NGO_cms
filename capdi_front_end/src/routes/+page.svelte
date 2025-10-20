<script lang="ts">
	import { goto } from '$app/navigation';

	function goToLogin() {
		goto('/auth/login');
	}
</script>

<main class="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-800 px-4 text-center">
	
	<h1 class="text-4xl sm:text-5xl font-bold text-blue-700 mb-6">
		CARING FOR PEOPLE WITH DISABILITIES
	</h1>




  <!-- Hero Image -->
	<!-- svelte-ignore a11y_img_redundant_alt -->
	<img
		src="/hero image.jpg"
		alt="Hero Image"
		class="w-full max-w-3xl rounded-xl shadow-lg mb-8 object-cover"
	/>

  	<p class="max-w-xl text-lg text-gray-600 mb-8 leading-relaxed">
		Welcome to our inclusive platform — empowering individuals with disabilities through
		community engagement, awareness, and support.
	</p>


	<button
		on:click={goToLogin}
		class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors"
	>
		Login
	</button>
</main>
