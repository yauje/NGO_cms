<script lang="ts">
  let name = "CARING FOR PEOPLE WITH DISABILITIES";
</script>

<main class="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-800">
  <h1 class="text-4xl font-bold text-blue-600 mb-4">
    {name}
  </h1>

  <p class="prose text-center max-w-prose">
    This app is powered by <strong>TailwindCSS</strong> with the <em>Typography</em> and <em>Forms</em> plugins.
  </p>

  <form class="mt-8 space-y-4 w-1/3">
    <input type="email" placeholder="Email" class="form-input w-full" />
    <input type="password" placeholder="Password" class="form-input w-full" />
    <button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition">
      Sign In
    </button>
  </form>
</main>
