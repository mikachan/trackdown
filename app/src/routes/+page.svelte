<script lang="ts">
	import { onMount } from 'svelte';
	import data from '#lib/data/coasters.json';
	import schedule from '#lib/data/schedule.json';
	import { decodeSchedule, londonDateKey, puzzleNumber, todaysAnswerId } from '#lib/day.ts';
	import { cluesFor, MAX_GUESSES, newGame, submitGuess, suggestionDetails, visibleClues, type GameState } from '#lib/game.ts';
	import { loadGame, loadStats, saveGame, saveResult, type Stats } from '#lib/storage.ts';
	import { shareText } from '#lib/share.ts';
	import { celebrate } from '#lib/confetti.ts';
	import { trackEvent } from '#lib/analytics.ts';
	import type { Coaster } from '#lib/types.ts';
	import Outline from '#lib/components/Outline.svelte';
	import GuessInput from '#lib/components/GuessInput.svelte';
	import ClueList from '#lib/components/ClueList.svelte';
	import AnswerCard from '#lib/components/AnswerCard.svelte';
	import StatsPanel from '#lib/components/StatsPanel.svelte';

	const coasters = data.coasters as Coaster[];
	const byId = new Map(coasters.map((c) => [c.id, c]));
	const details = suggestionDetails(coasters);
	const scheduleIds = decodeSchedule(schedule.days);

	let game = $state<GameState | null>(null);
	let stats = $state<Stats | null>(null);
	let puzzle = $state(1);
	let origin = $state('');

	const answer = $derived(game ? byId.get(game.answerId) : undefined);
	const clues = $derived(answer ? cluesFor(answer) : []);
	const wrongGuesses = $derived(
		game ? game.guesses.filter((id) => id !== game?.answerId).map((id) => byId.get(id)).filter((c) => c !== undefined) : []
	);

	function loadToday() {
		const dateKey = londonDateKey(new Date());
		const answerId = todaysAnswerId(dateKey, scheduleIds);
		const saved = loadGame(dateKey);
		puzzle = puzzleNumber(dateKey);
		game = saved && saved.answerId === answerId ? saved : newGame(dateKey, answerId);
		stats = loadStats();
	}

	/** A tab left open overnight moves on to the new puzzle when it's looked at again. */
	function checkForNewDay() {
		if (game && londonDateKey(new Date()) !== game.dateKey) loadToday();
	}

	onMount(() => {
		origin = location.origin;
		loadToday();
		const onVisible = () => document.visibilityState === 'visible' && checkForNewDay();
		document.addEventListener('visibilitychange', onVisible);
		window.addEventListener('focus', checkForNewDay);
		return () => {
			document.removeEventListener('visibilitychange', onVisible);
			window.removeEventListener('focus', checkForNewDay);
		};
	});

	function guess(id: string) {
		checkForNewDay();
		if (!game || game.status !== 'playing') return;
		game = submitGuess(game, id);
		saveGame(game);
		if (game.status !== 'playing') {
			stats = saveResult(game);
			trackEvent(game.status === 'won' ? 'daily-won' : 'daily-lost');
			if (game.status === 'won') celebrate();
		}
	}
</script>

<svelte:head>
	<title>Trackdown · guess the coaster</title>
</svelte:head>

<div class="daily">
	{#if game && answer?.path}
		<p class="meta">
			Trackdown #{puzzle}
			{#if game.status === 'playing'}· guess {game.guesses.length + 1} of {MAX_GUESSES}{/if}
		</p>

		{#if game.status === 'playing'}
			<Outline path={answer.path} />
			<ClueList {clues} visible={visibleClues(game, clues)} guesses={wrongGuesses} {details} />
			<GuessInput {coasters} {details} disabledIds={game.guesses} onguess={guess} />
		{:else}
			<AnswerCard coaster={answer} won={game.status === 'won'} />
			{#if stats}<StatsPanel {stats} shareText={shareText(game, puzzle, origin)} />{/if}
		{/if}
	{:else}
		<p class="loading">Loading today's coaster…</p>
	{/if}
</div>

<style>
	.daily {
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	.meta {
		margin: 0;
		text-align: center;
		color: var(--muted);
		font-weight: 600;
	}

	.loading {
		text-align: center;
		color: var(--muted);
		padding: 120px 0;
	}
</style>
