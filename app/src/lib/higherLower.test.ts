import { describe, expect, it } from 'vitest';
import { cardSubtitle, formatStat, hlPool, isCorrect, nextRound, QUESTIONS, type Stat } from './higherLower';
import type { Coaster } from './types';

function coaster(id: string, extra: Partial<Coaster> = {}): Coaster {
	return {
		id, name: id, park: 'Park', country: 'Country', opened: 2000, manufacturer: 'Maker', height_m: 40,
		speed_kmh: 100, length_m: 1000, inversions: 2, status: 'Operating', article: id, path: null, ...extra
	};
}

function seeded(seed: number): () => number {
	let s = seed + 1;
	const next = () => ((s = (s * 16807) % 2147483647) - 1) / 2147483646;
	for (let i = 0; i < 10; i++) next(); // small seeds start near 0; warm up first
	return next;
}

const SILVER_STAR = coaster('silver-star', { height_m: 73 });
const TARON = coaster('taron', { height_m: 30 });

// POOL[0] ties with some coasters on every stat, and one coaster is missing a stat.
const POOL: Coaster[] = [
	coaster('left'),
	coaster('same-height', { height_m: 40, speed_kmh: 120, length_m: 900, inversions: 0, opened: 2010 }),
	coaster('same-speed', { height_m: 60, speed_kmh: 100, length_m: 1500, inversions: 5, opened: 1990 }),
	coaster('same-everything'),
	coaster('different', { height_m: 80, speed_kmh: 140, length_m: 2000, inversions: 0, opened: 2020 }),
	coaster('missing-length', { height_m: 20, speed_kmh: 80, length_m: null, inversions: 1, opened: 1995 })
];

describe('nextRound', () => {
	it('never offers a tie or a missing value', () => {
		for (let i = 0; i < 500; i++) {
			const { stat, right } = nextRound(POOL, POOL[0], seeded(i));
			expect(right[stat]).not.toBeNull();
			expect(right[stat]).not.toBe(POOL[0][stat]);
			expect(right.id).not.toBe(POOL[0].id);
		}
	});

	it('never pairs values that look the same once rounded', () => {
		const left = coaster('left', { height_m: 62.5, speed_kmh: 100.4, length_m: 1000.2, inversions: 2, opened: 2000 });
		const lookalike = coaster('lookalike', { height_m: 62.8, speed_kmh: 99.6, length_m: 999.9, inversions: 2, opened: 2000 });
		for (let i = 0; i < 200; i++) {
			expect(() => nextRound([left, lookalike], left, seeded(i))).toThrow();
		}
	});

	it('changes stat between rounds', () => {
		for (let i = 0; i < 100; i++) {
			expect(nextRound(POOL, POOL[0], seeded(i), 'height_m').stat).not.toBe('height_m');
		}
	});

	it('uses every stat over many rounds', () => {
		const seen = new Set<Stat>();
		for (let i = 0; i < 200; i++) seen.add(nextRound(POOL, POOL[0], seeded(i)).stat);
		expect([...seen].sort()).toEqual(Object.keys(QUESTIONS).sort());
	});
});

describe('isCorrect', () => {
	it('judges higher and lower', () => {
		expect(isCorrect(SILVER_STAR, TARON, 'height_m', 'lower')).toBe(true);
		expect(isCorrect(SILVER_STAR, TARON, 'height_m', 'higher')).toBe(false);
		expect(isCorrect(TARON, SILVER_STAR, 'height_m', 'higher')).toBe(true);
	});
});

describe('hlPool', () => {
	it('pool excludes kiddie and incomplete coasters', () => {
		const kiddie = coaster('kiddie', { height_m: 8 });
		const short = coaster('short', { length_m: 200 });
		const noSpeed = coaster('no-speed', { speed_kmh: null });
		expect(hlPool([TARON, kiddie, short, noSpeed]).map((c) => c.id)).toEqual(['taron']);
	});
});

describe('formatStat', () => {
	it('formats each stat for the cards', () => {
		expect(formatStat('height_m', 73.2)).toBe('73 m');
		expect(formatStat('speed_kmh', 127.4)).toBe('127 km/h');
		expect(formatStat('length_m', 1620)).toBe('1,620 m');
		expect(formatStat('inversions', 3)).toBe('3');
		expect(formatStat('opened', 2002)).toBe('2002');
	});
});

describe('cardSubtitle', () => {
	it('hides the opening year on the hidden card in "opened later" rounds', () => {
		expect(cardSubtitle(TARON, 'opened', false)).toBe('Park');
		expect(cardSubtitle(TARON, 'opened', true)).toBe('Park · 2000');
		expect(cardSubtitle(TARON, 'height_m', false)).toBe('Park · 2000');
	});
});
