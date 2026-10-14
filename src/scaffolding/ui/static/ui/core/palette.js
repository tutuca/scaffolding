// The chart logic that runs without a browser, one concern per module: pure
// functions over the read models and color names `charts.py` emits, value in ->
// value out. Kept out of `charts/` (Plot, the document, getComputedStyle) so
// `node --test` can exercise each - see `tests/js/core/`.

// The chart palette, quoted from tokens.css's `--chart-*` names.
// Frozen: a record is a value, not a thing a caller reaches into and edits.
//
// `ahorro` is not a Bucket - it is `charts.py`'s name for the savings/surplus
// green, the same hue `income` draws. There is no `--chart-ahorro` token, so it
// quotes `--chart-income` rather than falling through to `--brand`.
export const BUCKET_TOKENS = Object.freeze({
  needs: "--chart-needs",
  wants: "--chart-wants",
  structural: "--chart-structural",
  income: "--chart-income",
  "sin decidir": "--chart-undecided",
  ahorro: "--chart-income",
});

// A color name `charts.py` emits - a bucket, or one of the ink names `ink`
// (dark), `muted` (quiet), `band` (light gray), `white`, `accent` - mapped to
// the CSS variable or literal that resolves it. The resolution itself
// (`getComputedStyle`) is `tokens.js`'s job; this is the pure half. ACCENT is
// spelled `sin decidir`, the bucket that already carries that red.
export function colorToken(name) {
  switch (name) {
    case "ink":
      return "--ink";
    case "muted":
      return "--ink-quiet";
    case "band":
      return "--line";
    case "white":
      return "#fff";
    case "accent":
      return "--chart-undecided";
    default:
      return BUCKET_TOKENS[name] ?? "--brand";
  }
}

// A color derived from one of the chart tokens, by turning its hue and nudging its
// saturation and lightness: a triad is +120 or +240, a complement +180, an
// analogous neighbour a few tens either way. The chart palette stays the five
// literals in tokens.css; anything else a figure needs is one of them, turned,
// so a new hue is an expression and not a sixth choice. `hex` is `#rrggbb`.
export function turned(hex, { hue = 0, sat = 1, light = 0 } = {}) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const lightness = (max + min) / 2;
  const span = max - min;
  const saturation = span === 0 ? 0 : span / (1 - Math.abs(2 * lightness - 1));
  let angle = 0;
  if (span !== 0) {
    if (max === r) angle = ((g - b) / span + 6) % 6;
    else if (max === g) angle = (b - r) / span + 2;
    else angle = (r - g) / span + 4;
  }
  const h = (((angle * 60 + hue) % 360) + 360) % 360;
  const s = Math.min(1, Math.max(0, saturation * sat));
  const l = Math.min(1, Math.max(0, lightness + light));
  const chroma = (1 - Math.abs(2 * l - 1)) * s;
  const x = chroma * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - chroma / 2;
  const [r1, g1, b1] = [[chroma, x, 0], [x, chroma, 0], [0, chroma, x], [0, x, chroma], [x, 0, chroma], [chroma, 0, x]][Math.floor(h / 60) % 6];
  return `#${[r1, g1, b1].map((v) => Math.round((v + m) * 255).toString(16).padStart(2, "0")).join("")}`;
}
