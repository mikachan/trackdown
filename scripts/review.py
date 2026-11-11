"""Build the local page Sarah uses to choose and order the daily puzzles.

Usage: python3 -I review.py <data/candidates.json> <review/review.html>
Open the page, approve and order coasters, then Export and save the file as data/schedule.json.
"""
import json
import os
import sys

TARGET = 60

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trackdown puzzle review</title>
<style>
:root { --bg:#faf8f5; --fg:#1d1b19; --muted:#6f6a64; --card:#fff; --line:#d6462c; --edge:#e8e3dc; --ok:#2e9e5b; --no:#9b958d; }
@media (prefers-color-scheme: dark) { :root { --bg:#161514; --fg:#eeeae4; --muted:#9b958d; --card:#211f1d; --line:#ff7a5c; --edge:#33302c; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:14px/1.4 system-ui, sans-serif; }
header { position:sticky; top:0; z-index:2; display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; padding:12px 16px; background:var(--bg); border-bottom:1px solid var(--edge); }
header h1 { font-size:18px; margin:0; } .count { font-weight:600; } .count.done { color:var(--ok); }
button { font:inherit; border:1px solid var(--edge); background:var(--card); color:var(--fg); border-radius:8px; padding:5px 10px; cursor:pointer; }
button.primary { background:var(--line); border-color:var(--line); color:#fff; }
.filters button[aria-pressed=true] { border-color:var(--fg); }
main { display:grid; grid-template-columns:minmax(260px, 340px) 1fr; gap:16px; padding:16px; }
@media (max-width:800px) { main { grid-template-columns:1fr; } }
h2 { font-size:15px; margin:0 0 8px; } .hint { color:var(--muted); font-size:12px; margin:0 0 8px; }
ol { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:4px; }
ol li { display:flex; align-items:center; gap:8px; background:var(--card); border:1px solid var(--edge); border-radius:8px; padding:4px 6px; cursor:grab; }
ol li.dragging { opacity:.4; } ol li .n { width:24px; text-align:right; color:var(--muted); font-variant-numeric:tabular-nums; }
ol li svg { width:34px; height:34px; flex:none; } ol li .nm { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
ol li button { padding:2px 6px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:12px; }
figure { margin:0; background:var(--card); border:2px solid var(--edge); border-radius:12px; padding:10px; display:flex; flex-direction:column; gap:6px; }
figure.approved { border-color:var(--ok); } figure.rejected { opacity:.45; }
figure svg { width:100%; aspect-ratio:1; }
svg path { fill:none; stroke:var(--line); stroke-width:1.6; stroke-linejoin:round; stroke-linecap:round; vector-effect:non-scaling-stroke; }
figure svg path { stroke-width:2.4; }
figcaption b { display:block; } figcaption span { display:block; color:var(--muted); font-size:12px; }
dl { display:grid; grid-template-columns:auto 1fr; gap:0 8px; margin:0; font-size:12px; } dt { color:var(--muted); } dd { margin:0; }
.actions { display:flex; gap:6px; } .actions button { flex:1; }
.actions .on.ok { background:var(--ok); border-color:var(--ok); color:#fff; } .actions .on.no { background:var(--no); border-color:var(--no); color:#fff; }
</style></head><body>
<header>
  <h1>Trackdown puzzle review</h1>
  <span class="count" id="count"></span>
  <span class="filters" role="group" aria-label="Show">
    <button data-filter="all" aria-pressed="true">All</button>
    <button data-filter="undecided" aria-pressed="false">Undecided</button>
    <button data-filter="approved" aria-pressed="false">Approved</button>
    <button data-filter="rejected" aria-pressed="false">Rejected</button>
  </span>
  <button class="primary" id="export">Export schedule.json</button>
</header>
<main>
  <section>
    <h2>Your schedule</h2>
    <p class="hint">Day 1 at the top. Drag to reorder, or use the arrows. Your progress saves in this browser.</p>
    <ol id="schedule"></ol>
  </section>
  <section><div class="grid" id="grid"></div></section>
</main>
<script>
const CANDIDATES = __DATA__;
const TARGET = __TARGET__;
const STORE = 'td-review-v1';
const byId = Object.fromEntries(CANDIDATES.map(c => [c.id, c]));
let state = { order: [], rejected: [] };
try { const saved = JSON.parse(localStorage.getItem(STORE)); if (saved && Array.isArray(saved.order)) state = saved; } catch (e) {}
state.order = state.order.filter(id => byId[id]);
let filter = 'all';
const save = () => { try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) {} };
const svg = c => `<svg viewBox="0 0 100 100" aria-hidden="true"><path d="${c.path}"/></svg>`;
const esc = s => String(s ?? '').replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
const status = id => state.order.includes(id) ? 'approved' : state.rejected.includes(id) ? 'rejected' : 'undecided';

function set(id, to) {
  state.order = state.order.filter(x => x !== id);
  state.rejected = state.rejected.filter(x => x !== id);
  if (to === 'approved') state.order.push(id);
  if (to === 'rejected') state.rejected.push(id);
  save(); render();
}
function move(i, delta) {
  const j = i + delta;
  if (j < 0 || j >= state.order.length) return;
  [state.order[i], state.order[j]] = [state.order[j], state.order[i]];
  save(); render();
}
function render() {
  const n = state.order.length;
  const count = document.getElementById('count');
  count.textContent = `Approved: ${n} / ${TARGET}`;
  count.classList.toggle('done', n >= TARGET);
  document.getElementById('schedule').innerHTML = state.order.map((id, i) =>
    `<li draggable="true" data-i="${i}"><span class="n">${i + 1}</span>${svg(byId[id])}<span class="nm">${esc(byId[id].name)}</span>` +
    `<button data-move="-1" aria-label="Move up">↑</button><button data-move="1" aria-label="Move down">↓</button></li>`).join('');
  document.getElementById('grid').innerHTML = CANDIDATES.filter(c => filter === 'all' || status(c.id) === filter).map(c => {
    const s = status(c.id);
    return `<figure class="${s}" data-id="${esc(c.id)}">${svg(c)}<figcaption><b>${esc(c.name)}</b><span>${esc(c.park)} · ${esc(c.country)}</span></figcaption>` +
      `<dl><dt>Opened</dt><dd>${c.opened}</dd><dt>Height</dt><dd>${Math.round(c.height_m)} m</dd><dt>Speed</dt><dd>${Math.round(c.speed_kmh)} km/h</dd><dt>Maker</dt><dd>${esc(c.manufacturer)}</dd></dl>` +
      `<div class="actions"><button data-set="approved" class="${s === 'approved' ? 'on ok' : ''}">Approve</button><button data-set="rejected" class="${s === 'rejected' ? 'on no' : ''}">Reject</button></div></figure>`;
  }).join('');
}
document.getElementById('grid').addEventListener('click', e => {
  const b = e.target.closest('button[data-set]'); if (!b) return;
  const id = b.closest('figure').dataset.id;
  set(id, status(id) === b.dataset.set ? 'undecided' : b.dataset.set);
});
const list = document.getElementById('schedule');
list.addEventListener('click', e => {
  const b = e.target.closest('button[data-move]'); if (!b) return;
  move(Number(b.closest('li').dataset.i), Number(b.dataset.move));
});
let dragFrom = null;
list.addEventListener('dragstart', e => { const li = e.target.closest('li'); dragFrom = Number(li.dataset.i); li.classList.add('dragging'); });
list.addEventListener('dragover', e => e.preventDefault());
list.addEventListener('drop', e => {
  e.preventDefault();
  const li = e.target.closest('li'); if (!li || dragFrom === null) return;
  const [id] = state.order.splice(dragFrom, 1);
  state.order.splice(Number(li.dataset.i), 0, id);
  dragFrom = null; save(); render();
});
list.addEventListener('dragend', () => { dragFrom = null; render(); });
document.querySelector('.filters').addEventListener('click', e => {
  const b = e.target.closest('button[data-filter]'); if (!b) return;
  filter = b.dataset.filter;
  document.querySelectorAll('.filters button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  render();
});
document.getElementById('export').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify({ ids: state.order }, null, 1)], { type: 'application/json' });
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'schedule.json' });
  a.click(); URL.revokeObjectURL(a.href);
});
render();
</script></body></html>
'''


def main(src, dst):
    candidates = json.load(open(src))
    data = json.dumps(candidates, ensure_ascii=False).replace('</', '<\\/')
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    open(dst, 'w').write(PAGE.replace('__DATA__', data).replace('__TARGET__', str(TARGET)))
    print('review page: %s (%d candidates)' % (dst, len(candidates)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
