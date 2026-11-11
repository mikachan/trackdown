<script lang="ts">
	import { searchCoasters } from '#lib/game.ts';
	import type { Coaster } from '#lib/types.ts';

	let {
		coasters,
		disabledIds,
		onguess
	}: { coasters: Coaster[]; disabledIds: string[]; onguess: (id: string) => void } = $props();

	let query = $state('');
	let open = $state(false);
	let active = $state(0);
	const results = $derived(searchCoasters(query, coasters, 12).filter((c) => !disabledIds.includes(c.id)).slice(0, 8));

	function choose(c: Coaster) {
		onguess(c.id);
		query = '';
		open = false;
		active = 0;
	}

	function keydown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown' && results.length) {
			e.preventDefault();
			open = true;
			active = (active + 1) % results.length;
		} else if (e.key === 'ArrowUp' && results.length) {
			e.preventDefault();
			active = (active - 1 + results.length) % results.length;
		} else if (e.key === 'Enter') {
			e.preventDefault();
			if (open && results[active]) choose(results[active]);
		} else if (e.key === 'Escape') {
			open = false;
		}
	}
</script>

<div class="combo">
	<label for="guess" class="visually-hidden">Guess the coaster</label>
	<input
		id="guess"
		type="text"
		role="combobox"
		autocomplete="off"
		spellcheck="false"
		placeholder="Type a coaster…"
		aria-autocomplete="list"
		aria-controls="guess-options"
		aria-expanded={open && results.length > 0}
		aria-activedescendant={open && results[active] ? `option-${results[active].id}` : undefined}
		bind:value={query}
		oninput={() => {
			open = true;
			active = 0;
		}}
		onkeydown={keydown}
		onblur={() => (open = false)}
	/>
	{#if open && results.length > 0}
		<ul id="guess-options" role="listbox" aria-label="Matching coasters">
			{#each results as c, i (c.id)}
				<li
					id="option-{c.id}"
					role="option"
					aria-selected={i === active}
					onmousedown={(e) => {
						e.preventDefault();
						choose(c);
					}}
				>
					<b>{c.name}</b>{#if c.park}<span>{` · ${c.park}`}</span>{/if}
				</li>
			{/each}
		</ul>
	{/if}
</div>

<style>
	.combo {
		position: relative;
	}

	input {
		width: 100%;
		font: inherit;
		padding: 12px 14px;
		border: 1px solid var(--edge);
		border-radius: var(--radius);
		background: var(--card);
		color: var(--fg);
	}

	ul {
		position: absolute;
		z-index: 5;
		left: 0;
		right: 0;
		bottom: calc(100% + 4px);
		margin: 0;
		padding: 4px;
		list-style: none;
		background: var(--card);
		border: 1px solid var(--edge);
		border-radius: var(--radius);
		box-shadow: 0 8px 24px rgb(0 0 0 / 0.12);
	}

	li {
		padding: 8px 10px;
		border-radius: 8px;
		cursor: pointer;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	li[aria-selected='true'] {
		background: var(--locked);
	}

	b {
		font-weight: 600;
	}

	span {
		color: var(--muted);
	}
</style>
