<script lang="ts">
	import { onMount } from 'svelte';
	import data from '#lib/data/coasters.json';
	import { formatStat, hlPool, isCorrect, nextRound, QUESTIONS, type Stat } from '#lib/higherLower.ts';
	import { bestHigherLower, saveBestHigherLower } from '#lib/storage.ts';
	import type { Coaster } from '#lib/types.ts';
	import HlCard from '#lib/components/HlCard.svelte';

	const REVEAL_MS = 900;
	const pool = hlPool(data.coasters as Coaster[]);

	let left = $state<Coaster | null>(null);
	let right = $state<Coaster | null>(null);
	let stat = $state<Stat>('height_m');
	let score = $state(0);
	let best = $state(0);
	let phase = $state<'choose' | 'reveal' | 'over'>('choose');

	function deal(from: Coaster, lastStat?: Stat) {
		const round = nextRound(pool, from, Math.random, lastStat);
		left = from;
		right = round.right;
		stat = round.stat;
		phase = 'choose';
	}

	function start() {
		score = 0;
		deal(pool[Math.floor(Math.random() * pool.length)]);
	}

	function choose(choice: 'higher' | 'lower') {
		if (!left || !right || phase !== 'choose') return;
		if (isCorrect(left, right, stat, choice)) {
			phase = 'reveal';
			score += 1;
			if (score > best) {
				best = score;
				saveBestHigherLower(best);
			}
			const next = right;
			setTimeout(() => deal(next, stat), REVEAL_MS);
		} else {
			phase = 'over';
		}
	}

	onMount(() => {
		best = bestHigherLower();
		start();
	});
</script>

<svelte:head>
	<title>Higher or Lower · Trackdown</title>
</svelte:head>

<div class="hl">
	<div class="scores"><span>Score {score}</span><span>Best {best}</span></div>

	{#if left && right}
		<p class="question">{QUESTIONS[stat]}</p>
		<div class="pair">
			<HlCard coaster={left} {stat} reveal />
			<span class="vs" aria-hidden="true">vs</span>
			<HlCard coaster={right} {stat} reveal={phase !== 'choose'}>
				{#if phase === 'choose'}
					<button class="btn" onclick={() => choose('higher')}>Higher</button>
					<button class="btn" onclick={() => choose('lower')}>Lower</button>
				{:else if phase === 'reveal'}
					<span class="verdict ok">Yes!</span>
				{:else}
					<span class="verdict">Not quite</span>
				{/if}
			</HlCard>
		</div>

		{#if phase === 'over'}
			<div class="over" aria-live="polite">
				<p>
					{right.name} is {formatStat(stat, right[stat] as number)}. You scored <b>{score}</b>{score >= best && score > 0 ? ', a new best!' : `. Best: ${best}`}
				</p>
				<button class="btn primary" onclick={start}>Play again</button>
			</div>
		{/if}
	{:else}
		<p class="loading">Picking two coasters…</p>
	{/if}
</div>

<style>
	.hl {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.scores {
		display: flex;
		justify-content: space-between;
		color: var(--muted);
		font-weight: 600;
	}

	.question {
		margin: 0;
		text-align: center;
		font-size: 1.3rem;
		font-weight: 700;
	}

	.pair {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		grid-template-rows: repeat(5, auto);
		column-gap: 12px;
	}

	.vs {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		background: var(--bg);
		border: 1px solid var(--edge);
		border-radius: 999px;
		padding: 2px 8px;
		font-size: 0.8rem;
		font-weight: 700;
		color: var(--muted);
	}

	.verdict {
		align-self: center;
		font-weight: 700;
		color: var(--muted);
	}

	.verdict.ok {
		color: var(--ok);
	}

	.over {
		text-align: center;
	}

	.over p {
		margin: 0 0 10px;
	}

	.loading {
		text-align: center;
		color: var(--muted);
		padding: 120px 0;
	}
</style>
