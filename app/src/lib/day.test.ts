import { describe, expect, it } from 'vitest';
import { answerIdFor, decodeSchedule, londonDateKey, previousDay, puzzleNumber } from './day';

// encode_schedule.encode(['taron-phantasialand'], 'trackdown-v1') from scripts/encode_schedule.py
const FIXTURE = 'ABMTDAVJHx8PQwJQBxsADwoKCw';
const POOL = Array.from({ length: 80 }, (_, i) => `coaster-${i}`);

function addDays(dateKey: string, n: number): string {
	const d = new Date(`${dateKey}T12:00:00Z`);
	d.setUTCDate(d.getUTCDate() + n);
	return d.toISOString().slice(0, 10);
}

describe('londonDateKey', () => {
	it('uses UK midnight, not local', () => {
		expect(londonDateKey(new Date('2026-07-01T23:30:00Z'))).toBe('2026-07-02'); // BST: 00:30 UK
		expect(londonDateKey(new Date('2026-12-01T23:30:00Z'))).toBe('2026-12-01'); // GMT: 23:30 UK
	});

	it('handles the clock-change days', () => {
		expect(londonDateKey(new Date('2026-03-29T00:30:00Z'))).toBe('2026-03-29');
		expect(londonDateKey(new Date('2026-10-24T23:30:00Z'))).toBe('2026-10-25');
	});
});

describe('puzzleNumber', () => {
	it('numbers puzzles from launch', () => {
		expect(puzzleNumber('2026-12-01', '2026-12-01')).toBe(1);
		expect(puzzleNumber('2027-01-30', '2026-12-01')).toBe(61);
	});

	it('counts days before launch as day 1', () => {
		expect(puzzleNumber('2026-11-20', '2026-12-01')).toBe(1);
	});
});

describe('previousDay', () => {
	it('steps back across month, year and clock-change boundaries', () => {
		expect(previousDay('2027-01-01')).toBe('2026-12-31');
		expect(previousDay('2026-03-01')).toBe('2026-02-28');
		expect(previousDay('2026-10-26')).toBe('2026-10-25');
	});
});

describe('schedule', () => {
	it('decodes what the Python encoder wrote', () => {
		expect(decodeSchedule([FIXTURE])).toEqual(['taron-phantasialand']);
	});

	it('uses the schedule while it lasts', () => {
		expect(answerIdFor('2026-12-02', ['a', 'b', 'c'], POOL, '2026-12-01')).toBe('b');
	});

	it('falls back deterministically after the schedule ends', () => {
		const a = answerIdFor('2027-06-01', ['x'], POOL, '2026-12-01');
		expect(answerIdFor('2027-06-01', ['x'], POOL, '2026-12-01')).toBe(a);
		expect(POOL).toContain(a);
	});

	it('does not repeat a fallback answer within 60 days', () => {
		const days = Array.from({ length: 200 }, (_, i) => answerIdFor(addDays('2026-12-02', i), ['x'], POOL, '2026-12-01'));
		for (let i = 0; i < days.length; i++) {
			expect(days.slice(Math.max(0, i - 59), i)).not.toContain(days[i]);
		}
	});
});
