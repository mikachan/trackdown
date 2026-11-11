<script lang="ts">
	import type { Clue } from '#lib/game.ts';
	import type { Coaster } from '#lib/types.ts';

	let { clues, visible, guesses }: { clues: Clue[]; visible: number; guesses: Coaster[] } = $props();
</script>

<ol class="rows">
	{#each guesses as g (g.id)}
		<li class="row wrong">
			<span><s>{g.name}</s>{#if g.park}<small>{` · ${g.park}`}</small>{/if}</span><span aria-label="wrong">✗</span>
		</li>
	{/each}
	{#each clues as clue, i (clue.label)}
		{#if i < visible}
			<li class="row clue"><span>{clue.label}</span><b>{clue.value}</b></li>
		{:else}
			<li class="row locked"><span>{clue.label}</span><span>after guess {i + 1}</span></li>
		{/if}
	{/each}
</ol>

<style>
	.rows {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.row {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		padding: 9px 12px;
		border-radius: 10px;
		background: var(--card);
		border: 1px solid var(--edge);
	}

	.wrong {
		color: var(--muted);
	}

	.wrong small {
		font-size: 0.85em;
	}

	.locked {
		background: var(--locked);
		color: var(--muted);
		font-style: italic;
	}

	b {
		font-weight: 650;
		text-align: right;
	}
</style>
