import { afterEach, describe, expect, it } from 'vitest';
import { countPage, trackEvent } from './analytics';

type Call = Record<string, unknown>;

function fakeGoatCounter(): Call[] {
	const calls: Call[] = [];
	(globalThis as Record<string, unknown>).goatcounter = { count: (vars: Call) => calls.push(vars) };
	return calls;
}

afterEach(() => {
	delete (globalThis as Record<string, unknown>).goatcounter;
});

describe('analytics', () => {
	it('sends events to GoatCounter as events', () => {
		const calls = fakeGoatCounter();
		trackEvent('daily-won');
		expect(calls).toEqual([{ path: 'daily-won', title: 'daily-won', event: true }]);
	});

	it('counts in-app page changes as page views', () => {
		const calls = fakeGoatCounter();
		countPage('/higher-or-lower');
		expect(calls).toEqual([{ path: '/higher-or-lower' }]);
	});

	it('does nothing when GoatCounter is blocked or not loaded', () => {
		expect(() => trackEvent('daily-won')).not.toThrow();
		expect(() => countPage('/')).not.toThrow();
	});

	it('never lets a GoatCounter error break the game', () => {
		(globalThis as Record<string, unknown>).goatcounter = {
			count: () => {
				throw new Error('boom');
			}
		};
		expect(() => trackEvent('shared')).not.toThrow();
	});
});
