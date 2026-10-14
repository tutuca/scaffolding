// The chart logic that runs without a browser, one concern per module: pure
// functions over the read models and color names `charts.py` emits, value in ->
// value out. Kept out of `charts/` (Plot, the document, getComputedStyle) so
// `node --test` can exercise each - see `tests/js/core/`.

// The pareto's single normalized axis: bars as a share of the largest (so the
// tallest is 100), and the cumulative curve as points over the same axis. The
// peso values live in each bar's caption; the axis is the accumulated percent.
export function paretoBars(rows, cumulative) {
  const max = Math.max(...rows.map((d) => d.value), 1);
  const bars = rows.map((d) => ({ ...d, width: (d.value / max) * 100 }));
  const points = rows.map((d, i) => ({ y: d.label, cum: cumulative[i] }));
  return { max, bars, points };
}

// The home's glance, reshaped into one bar per series per month: `ingresos` to
// the left of each month index, `egresos` to the right, half a bar either side.
export function flowBars(months, ingresos, egresos, ingresosCaptions, egresosCaptions) {
  return months.flatMap((period, i) => [
    { x1: i - 0.38, x2: i, labelX: i - 0.19, y: ingresos[i], caption: ingresosCaptions[i], series: "ingresos" },
    { x1: i, x2: i + 0.38, labelX: i + 0.19, y: egresos[i], caption: egresosCaptions[i], series: "egresos" },
  ]);
}
