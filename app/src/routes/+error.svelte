<script lang="ts">
	import { page } from '$app/state';
</script>

<svelte:head>
	<title>{page.status === 404 ? 'Not found' : 'Something went wrong'} · Trackdown</title>
</svelte:head>

<section>
	{#if page.status === 404}
		<h1>This track doesn't go anywhere</h1>
		<p>There's no page here.</p>
	{:else}
		<h1>Something went off the rails</h1>
		<p>Sorry about that. Try again in a moment.</p>
	{/if}
	<a class="btn primary" href="/">Back to today's coaster</a>
</section>

<style>
	section {
		text-align: center;
		padding: 64px 0;
	}

	h1 {
		font-size: 1.4rem;
		margin: 0 0 6px;
	}

	p {
		color: var(--muted);
		margin: 0 0 20px;
	}

	a {
		display: inline-block;
		text-decoration: none;
	}
</style>
