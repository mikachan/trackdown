<svelte:head>
	<title>About · Trackdown</title>
</svelte:head>

<article>
	<h1>Hello, coaster fans</h1>
	<p>
		Trackdown is a little guessing game for anyone who can spot their favourite ride from a mile away. Or from a
		few hundred metres up, anyway.
	</p>

	<h2>How to play</h2>
	<p>
		Each day there's a new mystery coaster, and everyone gets the same one. You'll see its track from above, with
		north at the top. Think you know it? Have a guess! You get six tries, and every miss unlocks a clue: when it
		opened, how tall it is, how fast it goes, who built it, and finally where it lives. A fresh coaster rolls in at
		midnight UK time.
	</p>

	<h2>Higher or Lower</h2>
	<p>
		Fancy a few more rides? Two coasters go head to head: which is taller, faster, longer, loopier or newer? See how
		long a streak you can keep going.
	</p>

	<h2>Thank you, open data</h2>
	<p>
		The track maps come from <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> (© OpenStreetMap
		contributors, under the Open Database Licence), and the stats come from
		<a href="https://en.wikipedia.org/">Wikipedia</a> (under
		<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>). Spot something wrong or missing?
		Fixing it on OpenStreetMap or Wikipedia makes it better for everyone, and it'll find its way here when the data's next refreshed.
	</p>

	<h2>Your streaks</h2>
	<p>
		Your streaks and scores live in your own browser, and there are no accounts. Visits are counted with
		<a href="https://www.goatcounter.com/">GoatCounter</a>, which doesn't use cookies.
	</p>

	<p class="made">
		Made by Sarah. Peek at the code on <a href="https://github.com/mikachan/trackdown">GitHub</a>.
	</p>
</article>

<style>
	h1 {
		font-size: 1.6rem;
		margin: 0 0 8px;
	}

	h2 {
		font-size: 1.1rem;
		margin: 20px 0 4px;
	}

	p {
		margin: 0;
	}

	.made {
		margin-top: 24px;
		color: var(--muted);
	}
</style>
