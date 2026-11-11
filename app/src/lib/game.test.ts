import { describe, expect, it } from 'vitest';
import { cluesFor, MAX_GUESSES, newGame, puzzlePool, searchCoasters, submitGuess, visibleClues } from './game';
import type { Coaster } from './types';

function coaster(id: string, name: string, park: string | null, extra: Partial<Coaster> = {}): Coaster {
	return {
		id, name, park, country: null, opened: null, manufacturer: null, height_m: null, speed_kmh: null,
		length_m: null, inversions: null, status: 'Operating', article: name, path: null, ...extra
	};
}

const GEFORCE = coaster('expedition-geforce-plopsaland-deutschland', 'Expedition GeForce', 'Plopsaland Deutschland', {
	country: 'Germany', opened: 2001, manufacturer: 'Intamin', height_m: 53, speed_kmh: 120.1
});

const ALL: Coaster[] = [
	coaster('goliath-walibi-holland', 'Goliath', 'Walibi Holland'),
	coaster('goliath-la-ronde', 'Goliath', 'La Ronde'),
	coaster('goliath-junior', 'Goliath Jr.', 'Somewhere'),
	coaster('flying-goliath', 'The Flying Goliath', 'Elsewhere'),
	coaster('fonix-farup-sommerland', 'Fønix', 'Fårup Sommerland'),
	coaster('the-smiler-alton-towers', 'The Smiler', 'Alton Towers'),
	GEFORCE
];

const play = (answer: string, guesses: string[]) =>
	guesses.reduce((s, g) => submitGuess(s, g), newGame('2026-12-01', answer));

describe('cluesFor', () => {
	it('orders clues and skips missing ones', () => {
		expect(cluesFor({ ...GEFORCE, speed_kmh: null }).map((c) => c.label)).toEqual([
			'Opened', 'Height', 'Manufacturer', 'Country & park'
		]);
	});

	it('formats clue values', () => {
		expect(cluesFor(GEFORCE).map((c) => c.value)).toEqual([
			'2001', '53 m', '120 km/h', 'Intamin', 'Germany · Plopsaland Deutschland'
		]);
	});

	it('shows whichever of country and park exists', () => {
		expect(cluesFor({ ...GEFORCE, country: null }).at(-1)?.value).toBe('Plopsaland Deutschland');
	});
});

describe('guesses', () => {
	it('judges by id, not name', () => {
		expect(play('goliath-walibi-holland', ['goliath-la-ronde']).status).toBe('playing');
	});

	it('wins on the right id', () => {
		expect(play('a', ['a']).status).toBe('won');
	});

	it('loses after six wrong guesses', () => {
		const s = play('answer', ['1', '2', '3', '4', '5', '6']);
		expect(MAX_GUESSES).toBe(6);
		expect(s.status).toBe('lost');
		expect(s.guesses).toHaveLength(6);
	});

	it('ignores duplicates and guesses after the end', () => {
		expect(play('answer', ['1', '1']).guesses).toEqual(['1']);
		expect(play('a', ['a', 'b']).guesses).toEqual(['a']);
	});

	it('unlocks one clue per wrong guess, and all clues at the end', () => {
		const clues = cluesFor(GEFORCE);
		expect(visibleClues(play('a', ['1', '2']), clues)).toBe(2);
		expect(visibleClues(play('a', ['a']), clues)).toBe(clues.length);
		expect(visibleClues(play('a', ['1', '2', '3', '4', '5', '6']), clues)).toBe(clues.length);
	});
});

describe('searchCoasters', () => {
	it('shows the park so same-name coasters can be told apart', () => {
		const parks = searchCoasters('goliath', ALL).map((c) => c.park);
		expect(parks).toContain('Walibi Holland');
		expect(parks).toContain('La Ronde');
	});

	it('ranks prefix matches first, then shorter names', () => {
		expect(searchCoasters('goliath', ALL).map((c) => c.name)).toEqual([
			'Goliath', 'Goliath', 'Goliath Jr.', 'The Flying Goliath'
		]);
	});

	it('matches without accents or "the"', () => {
		expect(searchCoasters('fonix', ALL)[0].name).toBe('Fønix');
		expect(searchCoasters('smiler', ALL)[0].name).toBe('The Smiler');
		expect(searchCoasters('THE SMI', ALL)[0].name).toBe('The Smiler');
	});

	it('needs at least two characters', () => {
		expect(searchCoasters('g', ALL)).toEqual([]);
	});
});

describe('puzzlePool', () => {
	it('only includes coasters with an outline and all five clues', () => {
		const withPath = { ...GEFORCE, path: 'M1,1 L2,2' };
		const noSpeed = { ...withPath, id: 'no-speed', speed_kmh: null };
		expect(puzzlePool([withPath, noSpeed, GEFORCE])).toEqual([withPath.id]);
	});
});
