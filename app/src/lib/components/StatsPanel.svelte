<script lang="ts">
	import type { Stats } from '#lib/storage.ts';

	let { stats, shareText }: { stats: Stats; shareText: string } = $props();

	let copied = $state(false);
	const winPct = $derived(stats.played ? Math.round((stats.won / stats.played) * 100) : 0);
	const most = $derived(Math.max(1, ...stats.guessCounts));

	async function share() {
		if (navigator.share) {
			try {
				await navigator.share({ text: shareText });
				return;
			} catch {
				// Cancelled or unsupported: fall back to copying.
			}
		}
		try {
			await navigator.clipboard.writeText(shareText);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		} catch {
			copied = false;
		}
	}
</script>

<section class="stats">
	<div class="numbers">
		<div><b>{stats.played}</b><span>Played</span></div>
		<div><b>{winPct}%</b><span>Won</span></div>
		<div><b>{stats.currentStreak}</b><span>Streak</span></div>
		<div><b>{stats.bestStreak}</b><span>Best</span></div>
	</div>
	<ol class="bars" aria-label="Wins by number of guesses">
		{#each stats.guessCounts as n, i (i)}
			<li>
				<span>{i + 1}</span>
				<div class="bar" style:width="{Math.max(8, (n / most) * 100)}%">{n}</div>
			</li>
		{/each}
	</ol>
	<div class="actions">
		<button class="btn primary" onclick={share}>{copied ? 'Copied!' : 'Share'}</button>
		<a class="btn" href="/higher-or-lower">Play Higher or Lower</a>
	</div>
</section>

<style>
	.stats {
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	.numbers {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		text-align: center;
	}

	.numbers b {
		display: block;
		font-size: 1.5rem;
	}

	.numbers span {
		color: var(--muted);
		font-size: 0.85rem;
	}

	.bars {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.bars li {
		display: grid;
		grid-template-columns: 16px 1fr;
		gap: 8px;
		align-items: center;
		font-size: 0.85rem;
	}

	.bar {
		background: var(--edge);
		border-radius: 4px;
		padding: 1px 6px;
		text-align: right;
		font-weight: 600;
	}

	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		justify-content: center;
	}

	.actions a {
		text-decoration: none;
	}
</style>
