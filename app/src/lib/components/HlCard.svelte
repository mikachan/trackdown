<script lang="ts">
	import type { Snippet } from 'svelte';
	import Outline from './Outline.svelte';
	import { cardSubtitle, formatStat, type Stat } from '#lib/higherLower.ts';
	import type { Coaster } from '#lib/types.ts';

	let {
		coaster,
		stat,
		reveal,
		children
	}: { coaster: Coaster; stat: Stat; reveal: boolean; children?: Snippet } = $props();
</script>

<!-- Five rows shared with the other card through subgrid, so both cards are always the same height. -->
<article class="card">
	<h2>{coaster.name}</h2>
	<p class="where">{cardSubtitle(coaster, stat, reveal)}</p>
	<div class="outline">
		{#if coaster.path}<Outline path={coaster.path} size="small" />{:else}<span class="no-map">No track map yet</span>{/if}
	</div>
	<p class="value" class:hidden={!reveal}>
		{reveal ? formatStat(stat, coaster[stat] as number) : '?'}
	</p>
	<div class="slot">{@render children?.()}</div>
</article>

<style>
	.card {
		grid-row: span 5;
		display: grid;
		grid-template-rows: subgrid;
		gap: 6px;
		padding: 12px;
		border-radius: var(--radius);
		background: var(--card);
		border: 1px solid var(--edge);
		grid-template-columns: minmax(0, 1fr);
		text-align: center;
		min-width: 0;
	}

	h2 {
		margin: 0;
		font-size: 1.05rem;
		line-height: 1.2;
		overflow-wrap: anywhere;
	}

	.where {
		margin: 0;
		color: var(--muted);
		font-size: 0.82rem;
	}

	.outline {
		aspect-ratio: 1;
		display: grid;
		place-items: center;
		border-radius: 8px;
		background: var(--locked);
	}

	.value {
		margin: 0;
		font-size: 1.6rem;
		font-weight: 700;
	}

	.value.hidden {
		color: var(--muted);
	}

	.no-map {
		color: var(--muted);
		font-size: 0.8rem;
	}

	.slot {
		display: flex;
		gap: 6px;
		justify-content: center;
		min-height: 40px;
	}

	.slot :global(.btn) {
		flex: 1;
		min-width: 0;
		padding: 8px 6px;
	}
</style>
