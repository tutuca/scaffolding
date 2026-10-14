// A what-if, merged into the page it was asked from.
//
// A grid whose rows move asks the server for the page as it would be with the new order and
// takes
// from the answer only what the order changes: the elements marked `data-preview="name"`
// (the sentence and the figure) and, in the grid, the cells of the columns marked
// `data-derived`, row by row by `data-key`. The rest of the page, and the order of the
// rows on screen, are the reader's and stay. Nothing is saved; the answer is a page like
// any other, so there is one derivation and no second one in the browser.
//
// Where to ask is the grid's to say, not this module's: `data-preview-url` is a URL with `{keys}`
// where the order goes (`/notebooks/planes?vista=metas&orden={keys}`), and an order with no
// keys - the saved page - is that URL without the parameters that are left empty.
//
// One ask at a time: a new one aborts the one still out, and `cancelPreview` aborts it
// without asking again (the caller no longer wants an answer).
let current;

export function cancelPreview() {
  current?.abort();
  current = undefined;
}

/** The page as it would be with `order` (goal keys, first to pay first), or as it is
 * saved when `order` is empty. Resolves "merged", "superseded" when it was cancelled or
 * a newer ask took its place (nothing to do), or "failed" when there was no answer to use. */
export async function preview(grid, order) {
  cancelPreview();
  const mine = new AbortController();
  current = mine;
  const url = new URL(grid.dataset.previewUrl.replace("{keys}", order.join(",")), location.origin);
  for (const [name, value] of [...url.searchParams]) if (value === "") url.searchParams.delete(name);
  let answer;
  try {
    const response = await fetch(url, { signal: mine.signal });
    answer = new DOMParser().parseFromString(await response.text(), "text/html");
  } catch {
    return mine.signal.aborted ? "superseded" : "failed";
  }
  if (current !== mine) return "superseded";
  current = undefined;
  const there = answer.querySelector(`data-grid#${grid.id}`);
  if (!there) return "failed";

  const drawn = [];
  for (const name of new Set([...document.querySelectorAll("[data-preview]")].map((node) => node.dataset.preview))) {
    const now = document.querySelector(`[data-preview="${name}"]`);
    const next = answer.querySelector(`[data-preview="${name}"]`);
    if (!now || !next) continue;
    const adopted = document.importNode(next, true);
    now.replaceWith(adopted);
    if (adopted.dataset.chart) drawn.push(adopted);
  }
  const derived = grid.columns.filter((column) => column.derived).map((column) => column.index);
  const incoming = new Map([...there.querySelector("tbody").rows].map((row) => [row.dataset.key, row]));
  for (const row of grid.natural) {
    const fresh = incoming.get(row.dataset.key);
    if (!fresh) continue;
    for (const index of derived) row.cells[index].innerHTML = fresh.cells[index].innerHTML;
  }
  if (drawn.length && window.Plot) await (await import("./charts/mount.js")).mountNodes(drawn);
  return "merged";
}
