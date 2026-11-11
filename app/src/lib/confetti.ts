/** One light confetti burst for a win. Skipped for people who prefer reduced motion. */
export async function celebrate(): Promise<void> {
	if (typeof window === 'undefined' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
	const { default: confetti } = await import('canvas-confetti');
	confetti({ particleCount: 120, spread: 75, origin: { y: 0.55 }, disableForReducedMotion: true });
}
