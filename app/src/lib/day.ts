/** Which day it is (in the UK), which puzzle number that is, and which coaster is the answer. */

/** Puzzle #1. A placeholder until Sarah picks the launch date. */
export const LAUNCH_DATE = '2026-12-01';

/** Must match KEY in scripts/encode_schedule.py. Light scrambling, not security. */
export const KEY = 'trackdown-v1';

const RECENT_DAYS = 60;
const londonFormat = new Intl.DateTimeFormat('en-CA', {
	timeZone: 'Europe/London',
	year: 'numeric',
	month: '2-digit',
	day: '2-digit'
});

export function londonDateKey(now: Date): string {
	return londonFormat.format(now);
}

function toUtcDay(dateKey: string): number {
	const [y, m, d] = dateKey.split('-').map(Number);
	return Date.UTC(y, m - 1, d) / 86_400_000;
}

function fromUtcDay(day: number): string {
	return new Date(day * 86_400_000).toISOString().slice(0, 10);
}

export function previousDay(dateKey: string): string {
	return fromUtcDay(toUtcDay(dateKey) - 1);
}

export function puzzleNumber(dateKey: string, launch = LAUNCH_DATE): number {
	return Math.max(1, toUtcDay(dateKey) - toUtcDay(launch) + 1);
}

export function decodeSchedule(days: string[], key = KEY): string[] {
	const k = new TextEncoder().encode(key);
	return days.map((day) => {
		const b64 = day.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (day.length % 4)) % 4);
		const bytes = Uint8Array.from(atob(b64), (ch, i) => ch.charCodeAt(0) ^ k[i % k.length]);
		return new TextDecoder().decode(bytes);
	});
}

function hash(s: string): number {
	let h = 2166136261;
	for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
	return h >>> 0;
}

function mulberry32(seed: number): () => number {
	let a = seed;
	return () => {
		a = (a + 0x6d2b79f5) | 0;
		let t = Math.imul(a ^ (a >>> 15), 1 | a);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

/**
 * Day n uses scheduleIds[n - 1]. After the schedule runs out, each day picks from the pool,
 * seeded by its date and skipping the previous 60 days' answers, so it's the same for everyone.
 */
export function answerIdFor(dateKey: string, scheduleIds: string[], poolIds: string[], launch = LAUNCH_DATE): string {
	const n = puzzleNumber(dateKey, launch);
	if (n <= scheduleIds.length) return scheduleIds[n - 1];

	const window = Math.min(RECENT_DAYS, poolIds.length - 1);
	const recent = scheduleIds.slice(-window);
	let answer = '';
	for (let k = scheduleIds.length + 1; k <= n; k++) {
		const day = fromUtcDay(toUtcDay(launch) + k - 1);
		const blocked = new Set(recent.slice(Math.max(0, recent.length - window)));
		const available = poolIds.filter((id) => !blocked.has(id));
		answer = available[Math.floor(mulberry32(hash(day))() * available.length)];
		recent.push(answer);
	}
	return answer;
}
