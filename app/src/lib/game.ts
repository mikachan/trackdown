/** The rules of Daily Trackdown: clues, guesses and coaster search. Pure functions, no storage. */
import type { Coaster } from './types';

export const MAX_GUESSES = 6;

export type Clue = { label: string; value: string };

export type GameState = {
	dateKey: string;
	answerId: string;
	guesses: string[];
	status: 'playing' | 'won' | 'lost';
};

/** Clue ladder, in order: opening year, height, speed, manufacturer, then country and park. */
export function cluesFor(c: Coaster): Clue[] {
	const clues: (Clue | null)[] = [
		c.opened !== null ? { label: 'Opened', value: String(c.opened) } : null,
		c.height_m !== null ? { label: 'Height', value: `${Math.round(c.height_m)} m` } : null,
		c.speed_kmh !== null ? { label: 'Top speed', value: `${Math.round(c.speed_kmh)} km/h` } : null,
		c.manufacturer ? { label: 'Manufacturer', value: c.manufacturer } : null,
		c.country || c.park ? { label: 'Country & park', value: [c.country, c.park].filter(Boolean).join(' · ') } : null
	];
	return clues.filter((clue): clue is Clue => clue !== null);
}

/** Coasters the daily puzzle can fall back to once Sarah's schedule runs out. */
export function puzzlePool(coasters: Coaster[]): string[] {
	return coasters
		.filter((c) => c.path && c.country && c.park && cluesFor(c).length === 5)
		.map((c) => c.id);
}

export function newGame(dateKey: string, answerId: string): GameState {
	return { dateKey, answerId, guesses: [], status: 'playing' };
}

export function submitGuess(state: GameState, guessId: string): GameState {
	if (state.status !== 'playing' || state.guesses.includes(guessId)) return state;
	const guesses = [...state.guesses, guessId];
	const status = guessId === state.answerId ? 'won' : guesses.length >= MAX_GUESSES ? 'lost' : 'playing';
	return { ...state, guesses, status };
}

export function visibleClues(state: GameState, clues: Clue[]): number {
	if (state.status !== 'playing') return clues.length;
	const wrong = state.guesses.filter((g) => g !== state.answerId).length;
	return Math.min(wrong, clues.length);
}

export function fold(s: string): string {
	return s
		.replace(/[øØ]/g, 'o')
		.replace(/[æÆ]/g, 'ae')
		.replace(/ß/g, 'ss')
		.normalize('NFKD')
		.replace(/[̀-ͯ]/g, '')
		.toLowerCase()
		.replace(/[^a-z0-9 ]+/g, ' ')
		.replace(/\s+/g, ' ')
		.trim()
		.replace(/^the /, '');
}

export function searchCoasters(query: string, coasters: Coaster[], limit = 8): Coaster[] {
	const q = fold(query);
	if (q.length < 2) return [];
	const hits: { c: Coaster; rank: number }[] = [];
	for (const c of coasters) {
		const name = fold(c.name);
		if (name.startsWith(q)) hits.push({ c, rank: 0 });
		else if (name.includes(q)) hits.push({ c, rank: 1 });
	}
	hits.sort((a, b) => a.rank - b.rank || a.c.name.length - b.c.name.length);
	return hits.slice(0, limit).map((h) => h.c);
}
