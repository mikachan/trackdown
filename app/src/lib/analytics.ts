/**
 * GoatCounter (cookie-free, open source). The script in +layout.svelte counts the first page load;
 * these helpers count in-app page changes and a few game events. They do nothing if the script is
 * blocked or hasn't loaded, and never let an analytics error reach the game.
 */
type GoatCounter = { count: (vars: Record<string, unknown>) => void };

function goatcounter(): GoatCounter | undefined {
	return (globalThis as { goatcounter?: GoatCounter }).goatcounter;
}

function send(vars: Record<string, unknown>): void {
	try {
		goatcounter()?.count?.(vars);
	} catch {
		// Analytics must never break the game.
	}
}

export function countPage(path: string): void {
	send({ path });
}

export function trackEvent(name: 'daily-won' | 'daily-lost' | 'shared' | (string & {})): void {
	send({ path: name, title: name, event: true });
}
