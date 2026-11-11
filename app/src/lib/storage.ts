/**
 * Progress saved in the player's browser. Storage can be missing, blocked, full or hold junk
 * (private windows, old formats), so every read falls back to defaults and every write may quietly fail.
 */
import { previousDay } from './day';
import { MAX_GUESSES, type GameState } from './game';

export type Stats = {
	played: number;
	won: number;
	currentStreak: number;
	bestStreak: number;
	lastWonDate: string | null;
	lastPlayedDate: string | null;
	/** Index 0..5 = won in 1..6 guesses. */
	guessCounts: number[];
};

const GAME_KEY = 'td:game';
const STATS_KEY = 'td:stats';
const HL_BEST_KEY = 'td:hl-best';

const defaultStats = (): Stats => ({
	played: 0, won: 0, currentStreak: 0, bestStreak: 0, lastWonDate: null, lastPlayedDate: null,
	guessCounts: Array(MAX_GUESSES).fill(0)
});

function defaultStore(): Storage | undefined {
	try {
		return globalThis.localStorage;
	} catch {
		return undefined;
	}
}

function read(key: string, store: Storage | undefined): unknown {
	try {
		const raw = store?.getItem(key);
		return raw == null ? null : JSON.parse(raw);
	} catch {
		return null;
	}
}

function write(key: string, value: unknown, store: Storage | undefined): void {
	try {
		store?.setItem(key, JSON.stringify(value));
	} catch {
		// Full or blocked storage: the game still works, it just won't remember.
	}
}

const isCount = (n: unknown) => typeof n === 'number' && Number.isInteger(n) && n >= 0;
const isDateOrNull = (d: unknown) => d === null || (typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d));

export function loadGame(dateKey: string, store = defaultStore()): GameState | null {
	const g = read(GAME_KEY, store) as GameState | null;
	const valid =
		g !== null && typeof g === 'object' && g.dateKey === dateKey && typeof g.answerId === 'string' &&
		Array.isArray(g.guesses) && g.guesses.every((x) => typeof x === 'string') &&
		['playing', 'won', 'lost'].includes(g.status);
	return valid ? g : null;
}

export function saveGame(state: GameState, store = defaultStore()): void {
	write(GAME_KEY, state, store);
}

export function loadStats(store = defaultStore()): Stats {
	const s = read(STATS_KEY, store) as Stats | null;
	const valid =
		s !== null && typeof s === 'object' &&
		[s.played, s.won, s.currentStreak, s.bestStreak].every(isCount) &&
		isDateOrNull(s.lastWonDate) && isDateOrNull(s.lastPlayedDate) &&
		Array.isArray(s.guessCounts) && s.guessCounts.length === MAX_GUESSES && s.guessCounts.every(isCount);
	return valid ? s : defaultStats();
}

export function saveStats(stats: Stats, store = defaultStore()): void {
	write(STATS_KEY, stats, store);
}

export function recordResult(stats: Stats, state: GameState): Stats {
	if (state.status === 'playing' || stats.lastPlayedDate === state.dateKey) return stats;
	const next = { ...stats, guessCounts: [...stats.guessCounts], played: stats.played + 1, lastPlayedDate: state.dateKey };
	if (state.status === 'won') {
		next.won += 1;
		next.guessCounts[state.guesses.length - 1] += 1;
		next.currentStreak = stats.lastWonDate === previousDay(state.dateKey) ? stats.currentStreak + 1 : 1;
		next.bestStreak = Math.max(stats.bestStreak, next.currentStreak);
		next.lastWonDate = state.dateKey;
	} else {
		next.currentStreak = 0;
	}
	return next;
}

export function bestHigherLower(store = defaultStore()): number {
	const n = read(HL_BEST_KEY, store);
	return isCount(n) ? (n as number) : 0;
}

export function saveBestHigherLower(n: number, store = defaultStore()): void {
	write(HL_BEST_KEY, n, store);
}
