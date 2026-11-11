/** Rules for Higher or Lower: which coasters can appear, and how each round is picked. */
import type { Coaster } from './types';

export type Stat = 'height_m' | 'speed_kmh' | 'length_m' | 'inversions' | 'opened';

export const QUESTIONS: Record<Stat, string> = {
	height_m: 'Which is taller?',
	speed_kmh: 'Which is faster?',
	length_m: 'Which is longer?',
	inversions: 'Which has more inversions?',
	opened: 'Which opened later?'
};

const STATS = Object.keys(QUESTIONS) as Stat[];

/** Coasters with every stat, minus kiddie coasters (same rule as is_kiddie in scripts/export.py). */
export function hlPool(coasters: Coaster[]): Coaster[] {
	return coasters.filter(
		(c) => STATS.every((s) => c[s] !== null) && (c.height_m as number) >= 10 && (c.length_m as number) >= 250
	);
}

/** A new right-hand coaster and stat to compare against `left`: never a tie, never missing, never the same stat twice. */
export function nextRound(pool: Coaster[], left: Coaster, rng: () => number, lastStat?: Stat): { stat: Stat; right: Coaster } {
	const stats = STATS.filter((s) => s !== lastStat);
	const start = Math.floor(rng() * stats.length);
	for (let i = 0; i < stats.length; i++) {
		const stat = stats[(start + i) % stats.length];
		// Compare what the player sees: 62.5 m and 62.8 m both show as "63 m", so that's a tie too.
		const shown = formatStat(stat, left[stat] as number);
		const options = pool.filter(
			(c) => c.id !== left.id && c[stat] !== null && formatStat(stat, c[stat] as number) !== shown
		);
		if (options.length) return { stat, right: options[Math.floor(rng() * options.length)] };
	}
	throw new Error('Higher or Lower pool is too small');
}

export function formatStat(stat: Stat, value: number): string {
	switch (stat) {
		case 'height_m':
			return `${Math.round(value)} m`;
		case 'speed_kmh':
			return `${Math.round(value)} km/h`;
		case 'length_m':
			return `${Math.round(value).toLocaleString('en-GB')} m`;
		default:
			return String(value);
	}
}

/** Park and year under the name. The year is hidden on the unrevealed card when the question is about it. */
export function cardSubtitle(coaster: Coaster, stat: Stat, reveal: boolean): string {
	const year = stat === 'opened' && !reveal ? null : coaster.opened;
	return [coaster.park, year].filter(Boolean).join(' · ');
}

export function isCorrect(left: Coaster, right: Coaster, stat: Stat, choice: 'higher' | 'lower'): boolean {
	const higher = (right[stat] as number) > (left[stat] as number);
	return choice === 'higher' ? higher : !higher;
}
