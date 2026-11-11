import { describe, expect, it } from 'vitest';
import { newGame, submitGuess, type GameState } from './game';
import {
	bestHigherLower, loadGame, loadStats, recordResult, saveBestHigherLower, saveGame, saveResult, saveStats, type Stats
} from './storage';

function memoryStore(initial: Record<string, string> = {}): Storage {
	const data = { ...initial };
	return {
		getItem: (k: string) => (k in data ? data[k] : null),
		setItem: (k: string, v: string) => void (data[k] = v),
		removeItem: (k: string) => void delete data[k],
		clear: () => Object.keys(data).forEach((k) => delete data[k]),
		key: (i: number) => Object.keys(data)[i] ?? null,
		get length() { return Object.keys(data).length; }
	};
}

const broken = {
	getItem() { throw new Error('denied'); },
	setItem() { throw new Error('full'); }
} as unknown as Storage;

const won = (dateKey: string, guesses = ['a']): GameState =>
	guesses.reduce((s, g) => submitGuess(s, g), newGame(dateKey, 'a'));
const lost = (dateKey: string): GameState =>
	['1', '2', '3', '4', '5', '6'].reduce((s, g) => submitGuess(s, g), newGame(dateKey, 'a'));
const record = (stats: Stats, ...games: GameState[]) => games.reduce((s, g) => recordResult(s, g), stats);

describe('saving a game', () => {
	it('restores today, ignores yesterday', () => {
		const store = memoryStore();
		const game = submitGuess(newGame('2026-12-01', 'a'), 'b');
		saveGame(game, store);
		expect(loadGame('2026-12-01', store)).toEqual(game);
		expect(loadGame('2026-12-02', store)).toBeNull();
	});

	it('survives storage that throws', () => {
		expect(loadStats(broken).played).toBe(0);
		expect(loadGame('2026-12-01', broken)).toBeNull();
		expect(bestHigherLower(broken)).toBe(0);
		expect(() => saveGame(newGame('d', 'a'), broken)).not.toThrow();
		expect(() => saveStats(loadStats(broken), broken)).not.toThrow();
		expect(() => saveBestHigherLower(3, broken)).not.toThrow();
	});

	it('survives corrupt or old-format data', () => {
		const store = memoryStore({ 'td:game': '{oops', 'td:stats': '{"played":"lots"}', 'td:hl-best': 'nope' });
		expect(loadGame('2026-12-01', store)).toBeNull();
		expect(loadStats(store)).toEqual(loadStats(memoryStore()));
		expect(bestHigherLower(store)).toBe(0);
	});
});

describe('streaks', () => {
	it('continues a streak only on consecutive days', () => {
		let s = record(loadStats(memoryStore()), won('2026-12-01'), won('2026-12-02'));
		expect(s.currentStreak).toBe(2);
		s = record(s, won('2026-12-04'));
		expect(s.currentStreak).toBe(1);
		expect(s.bestStreak).toBe(2);
	});

	it('a loss resets the streak but not the best', () => {
		const s = record(loadStats(memoryStore()), won('2026-12-01'), won('2026-12-02'), lost('2026-12-03'));
		expect(s.currentStreak).toBe(0);
		expect(s.bestStreak).toBe(2);
		expect(s.played).toBe(3);
		expect(s.won).toBe(2);
	});

	it('records a day only once', () => {
		const s = record(loadStats(memoryStore()), won('2026-12-01'), won('2026-12-01'));
		expect(s.played).toBe(1);
		expect(s.currentStreak).toBe(1);
	});

	it('counts how many guesses each win took', () => {
		const s = record(loadStats(memoryStore()), won('2026-12-01', ['x', 'a']));
		expect(s.guessCounts).toEqual([0, 1, 0, 0, 0, 0]);
	});

	it('ignores games still in progress', () => {
		const stats = loadStats(memoryStore());
		expect(recordResult(stats, newGame('2026-12-01', 'a'))).toEqual(stats);
	});

	it('round-trips through storage', () => {
		const store = memoryStore();
		const s = record(loadStats(store), won('2026-12-01'));
		saveStats(s, store);
		expect(loadStats(store)).toEqual(s);
	});
});

describe('higher or lower best score', () => {
	it('saves and loads', () => {
		const store = memoryStore();
		saveBestHigherLower(7, store);
		expect(bestHigherLower(store)).toBe(7);
	});
});

describe('fixes from review: stale tabs', () => {
	it('does not record a day older than the last one played', () => {
		const tuesday = record(loadStats(memoryStore()), won('2026-12-01'), won('2026-12-02'));
		expect(recordResult(tuesday, won('2026-12-01'))).toEqual(tuesday);
	});

	it('saveResult builds on what is in storage now, not on stats loaded earlier', () => {
		const store = memoryStore();
		saveStats(record(loadStats(store), won('2026-12-01'), won('2026-12-02')), store);
		const saved = saveResult(won('2026-12-03'), store);
		expect(saved.currentStreak).toBe(3);
		expect(loadStats(store).played).toBe(3);
	});
});
