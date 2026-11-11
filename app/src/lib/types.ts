/** One coaster, as exported by scripts/export.py into src/lib/data/coasters.json. */
export interface Coaster {
	id: string;
	name: string;
	park: string | null;
	country: string | null;
	opened: number | null;
	manufacturer: string | null;
	height_m: number | null;
	speed_kmh: number | null;
	length_m: number | null;
	inversions: number | null;
	status: string | null;
	article: string;
	/** SVG path data for a 0 0 100 100 viewBox, or null when there's no good outline. */
	path: string | null;
}
