import { describe, expect, it } from 'vitest';
import { shareText } from './share';
import type { GameState } from './game';

const URL = 'https://trackdown.sekai.co.uk';
const game = (guesses: string[], status: GameState['status']): GameState => ({
	dateKey: '2026-12-12', answerId: 'taron-phantasialand', guesses, status
});

describe('shareText', () => {
	it('share text has no spoilers', () => {
		const t = shareText(game(['x', 'y', 'taron-phantasialand'], 'won'), 12, URL);
		expect(t).toBe('Trackdown #12 🎢 got it with 2 clues\nhttps://trackdown.sekai.co.uk');
		expect(t.toLowerCase()).not.toContain('taron');
	});

	it('uses the singular for one clue', () => {
		expect(shareText(game(['x', 'taron-phantasialand'], 'won'), 3, URL)).toBe(`Trackdown #3 🎢 got it with 1 clue\n${URL}`);
	});

	it('celebrates a first-try win', () => {
		expect(shareText(game(['taron-phantasialand'], 'won'), 3, URL)).toBe(`Trackdown #3 🎢 got it first try!\n${URL}`);
	});

	it('says when it was missed', () => {
		expect(shareText(game(['1', '2', '3', '4', '5', '6'], 'lost'), 4, URL)).toBe(`Trackdown #4 🎢 missed it\n${URL}`);
	});
});
