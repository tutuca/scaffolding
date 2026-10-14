// The chart logic that runs without a browser, one concern per module: pure
// functions over the read models and color names `charts.py` emits, value in ->
// value out. Kept out of `charts/` (Plot, the document, getComputedStyle) so
// `node --test` can exercise each - see `tests/js/core/`.

// The chart scale: the figures are set a notch below the prose — a whole 1.25
// step down is 0.8em, and its captions at 0.64em came out too small to read — so
// the chart base is 0.9em and a caption is one step below *that*. Every measure
// in a figure — the row height, the label column, the edge padding — is a
// multiple of that base, sized so the layout does not move when the type does.
// `chartPx` turns a count of chart ems into pixels; the DOM modules hand it the
// page's own font size at mount, so the figures follow a reader's chosen size
// rather than one invented in the dark.
export const CHART_EM = 0.9;
export function chartPx(em, pagePx = 16) {
  return Math.round(pagePx * CHART_EM * em);
}
