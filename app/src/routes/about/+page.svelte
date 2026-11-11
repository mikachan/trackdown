<svelte:head>
	<title>About · Trackdown</title>
</svelte:head>

<article>
	<h1>About Trackdown</h1>

	<h2>Daily Trackdown</h2>
	<p>
		Every day there's a new roller coaster to find, the same one for everyone. All you get is its track, seen from
		above with north at the top. You have six guesses. Each wrong guess unlocks a clue: when it opened, how tall it is,
		its top speed, who built it, and finally where it is. A new coaster arrives at midnight UK time.
	</p>

	<h2>Higher or Lower</h2>
	<p>
		Two coasters, one question: which is taller, faster, longer, loopier or newer? Keep going until you get one wrong.
	</p>

	<h2>Where the data comes from</h2>
	<p>
		Track outlines come from <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, © OpenStreetMap
		contributors, available under the Open Database Licence. Coaster stats come from
		<a href="https://en.wikipedia.org/">Wikipedia</a> articles, available under
		<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Spotted a mistake? Fixing it on
		OpenStreetMap or Wikipedia helps everyone.
	</p>

	<h2>Your progress</h2>
	<p>Streaks and scores stay in your browser. There are no accounts and no tracking.</p>

	<p class="made">
		Made by Sarah. The code is on <a href="https://github.com/mikachan/trackdown">GitHub</a>.
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
