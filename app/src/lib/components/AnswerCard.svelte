<script lang="ts">
	import Outline from './Outline.svelte';
	import type { Coaster } from '#lib/types.ts';

	let { coaster, won }: { coaster: Coaster; won: boolean } = $props();

	const facts = $derived(
		[
			['Park', coaster.park],
			['Country', coaster.country],
			['Opened', coaster.opened],
			['Height', coaster.height_m !== null ? `${Math.round(coaster.height_m)} m` : null],
			['Top speed', coaster.speed_kmh !== null ? `${Math.round(coaster.speed_kmh)} km/h` : null],
			['Length', coaster.length_m !== null ? `${Math.round(coaster.length_m).toLocaleString('en-GB')} m` : null],
			['Inversions', coaster.inversions],
			['Manufacturer', coaster.manufacturer]
		].filter(([, v]) => v !== null && v !== undefined) as [string, string | number][]
	);
	const wiki = $derived(`https://en.wikipedia.org/wiki/${encodeURIComponent(coaster.article.replace(/ /g, '_'))}`);
</script>

<section class="card" aria-live="polite">
	<p class="kicker">{won ? 'You got it!' : 'This one was…'}</p>
	<h2>{coaster.name}</h2>
	{#if coaster.path}<Outline path={coaster.path} />{/if}
	<dl>
		{#each facts as [label, value] (label)}
			<dt>{label}</dt>
			<dd>{value}</dd>
		{/each}
	</dl>
	<a href={wiki} target="_blank" rel="noopener">Read about it on Wikipedia</a>
</section>

<style>
	.card {
		background: var(--card);
		border: 1px solid var(--edge);
		border-radius: var(--radius);
		padding: 16px;
		text-align: center;
	}

	.kicker {
		margin: 0;
		color: var(--muted);
		font-weight: 600;
	}

	h2 {
		margin: 2px 0 8px;
		font-size: 1.6rem;
	}

	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 4px 12px;
		margin: 12px 0;
		text-align: left;
	}

	dt {
		color: var(--muted);
	}

	dd {
		margin: 0;
		font-weight: 600;
	}
</style>
