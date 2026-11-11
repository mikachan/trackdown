<script lang="ts">
	let { path, size = 'large' }: { path: string; size?: 'large' | 'small' } = $props();
</script>

<svg class={size} viewBox="0 0 100 100" role="img" aria-label="Coaster track outline">
	<path d={path} />
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		aspect-ratio: 1;
	}

	svg.large {
		max-width: 320px;
		margin: 0 auto;
	}

	path {
		fill: none;
		stroke: var(--track);
		stroke-width: 1.4;
		stroke-linejoin: round;
		stroke-linecap: round;
	}

	.small path {
		stroke-width: 2.2;
	}
</style>
