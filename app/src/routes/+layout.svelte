<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	const description = 'Guess the roller coaster from its track. A new one every day.';
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="description" content={description} />
	<meta property="og:title" content="Trackdown" />
	<meta property="og:description" content={description} />
	<meta property="og:image" content="/og.png" />
	<meta property="og:type" content="website" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="theme-color" content="#d6462c" />
</svelte:head>

<header>
	<a class="wordmark" href="/">Trackdown</a>
	<nav aria-label="Games">
		<a href="/" aria-current={page.url.pathname === '/' ? 'page' : undefined}>Daily</a>
		<a href="/higher-or-lower" aria-current={page.url.pathname === '/higher-or-lower' ? 'page' : undefined}>
			Higher or Lower
		</a>
	</nav>
</header>

<main>
	{@render children()}
</main>

<footer>
	Track data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> (ODbL) ·
	Stats from <a href="https://en.wikipedia.org/">Wikipedia</a> (CC BY-SA) · <a href="/about">About</a> ·
	<a href="https://sekai.co.uk">sekai.co.uk</a>
</footer>

<style>
	header,
	main,
	footer {
		max-width: 520px;
		margin: 0 auto;
		padding-left: 16px;
		padding-right: 16px;
	}

	header {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		justify-content: space-between;
		gap: 4px 16px;
		padding-top: 16px;
		padding-bottom: 8px;
	}

	.wordmark {
		font-size: 1.5rem;
		font-weight: 800;
		letter-spacing: -0.02em;
		color: var(--accent);
		text-decoration: none;
	}

	nav {
		display: flex;
		gap: 14px;
	}

	nav a {
		color: var(--muted);
		text-decoration: none;
		font-weight: 600;
	}

	nav a[aria-current='page'] {
		color: var(--fg);
		text-decoration: underline;
		text-decoration-color: var(--accent);
		text-underline-offset: 4px;
		text-decoration-thickness: 2px;
	}

	main {
		padding-top: 8px;
		padding-bottom: 40px;
	}

	footer {
		padding-bottom: 32px;
		color: var(--muted);
		font-size: 0.8rem;
		text-align: center;
	}
</style>
