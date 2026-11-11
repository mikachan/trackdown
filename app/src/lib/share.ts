import type { GameState } from './game';

/** Spoiler-free share text: never includes the coaster. */
export function shareText(state: GameState, puzzle: number, url: string): string {
	const clues = state.guesses.length - 1;
	const result =
		state.status !== 'won' ? 'missed it'
		: clues === 0 ? 'got it first try!'
		: `got it with ${clues} ${clues === 1 ? 'clue' : 'clues'}`;
	return `Trackdown #${puzzle} 🎢 ${result}\n${url}`;
}
