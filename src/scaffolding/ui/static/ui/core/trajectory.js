// The trajectory's arithmetic, apart from its marks: where each layer of a month's
// column starts and stops, where the axis labels go, and where the seams are.
// Pure - value in, value out - so `node --test` can hold the shape the three
// panels are drawn from. See `tests/js/core/trajectory.test.js`.

// The layers of a month, bottom to top: what was chosen, then cash and fees, then what was
// committed. Money that left for an account the books cannot see is `undecided` among them. What is left after them is `saved`, drawn
// on top as the green that reaches the income - or, when the month overspent, the
// red that sticks out above it.
export const LAYERS = ["needs", "wants", "undecided", "other", "committed"];

const MONTH_NAMES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

// A month's column, as one rectangle per layer: the layers stacked from zero, and
// then the margin. `top` is what the month spent and committed in all; `saved`
// above zero fills from there up to the income, below zero it is the overshoot
// from the income up to `top`. A zero-height layer is left out: nothing to draw.
export function columns(data) {
  return data.months.flatMap((period, i) => {
    const observed = i < data.seen;
    let base = 0;
    const rects = LAYERS.map((layer) => {
      const rect = { i, period, observed, layer, y1: base, y2: base + data[layer][i] };
      base = rect.y2;
      return rect;
    });
    const margin =
      data.saved[i] >= 0
        ? { i, period, observed, layer: "saved", y1: base, y2: data.income[i] }
        : { i, period, observed, layer: "short", y1: data.income[i], y2: base };
    return [...rects, margin].filter((rect) => rect.y2 - rect.y1 > 0);
  });
}

// The tallest a column reaches: the larger of what came in and what left.
export function crest(data) {
  return Math.max(...data.months.map((_, i) => Math.max(data.income[i], LAYERS.reduce((sum, layer) => sum + data[layer][i], 0))));
}

// The axis's ticks: the first month of each `every` months (a quarter by default),
// which is where a reader looks for a date. The January one carries the year, the
// others only the month.
export function quarterTicks(months, every = 3) {
  return months.map((_, i) => i).filter((i) => (Number(months[i].slice(5)) - 1) % every === 0);
}

export function tickLabel(period) {
  const month = Number(period.slice(5)) - 1;
  return month === 0 ? `${MONTH_NAMES[month]} ${period.slice(2, 4)}` : MONTH_NAMES[month];
}

// A calendar year starts between its December and the January after it: the x of
// that seam, for the rule that separates the years.
export function yearSeams(months) {
  return months.map((_, i) => i).filter((i) => i > 0 && months[i].endsWith("-01")).map((i) => i - 0.5);
}

// A line that changes style where the plan begins: the observed stretch, and the
// planned one starting from the last observed point so the two meet.
export function seamed(values, seen) {
  const points = values.map((y, x) => (y == null ? null : { x, y })).filter(Boolean);
  return { observed: points.filter((p) => p.x < seen), planned: points.filter((p) => p.x >= seen - 1) };
}

// The room a scale needs, from its values, padded by a fraction of its own span.
export function padded(values, pad = 0.08) {
  const low = Math.min(...values);
  const high = Math.max(...values);
  const span = high - low || 1;
  return [low - span * pad, high + span * pad];
}

// What a hover says about one month: the figures a reader would otherwise have to
// read off three panels, in millions.
export function describe(data, i) {
  const millions = (value) => `${(value / 1e6).toFixed(1)} M`;
  const kind = i < data.seen ? "observado" : "proyectado";
  const lines = [
    `${data.months[i]} · ${kind}`,
    `ingreso ${millions(data.income[i])}`,
    `necesito ${millions(data.needs[i])} · quiero ${millions(data.wants[i])} · sin decidir ${millions(data.undecided[i])}`,
    `efectivo y cargos ${millions(data.other[i])} · comprometido ${millions(data.committed[i])}`,
    `ahorro ${millions(data.saved[i])} (${data.rate[i].toFixed(0)}%)`,
    `acumulado ${millions(data.cumulative[i])}`,
  ];
  if (data.nominal) lines.splice(1, 0, `en pesos del mes: ingreso ${millions(data.nominal.income[i])} · gasto ${millions(data.nominal.out[i])}`);
  if (data.band[i]) lines.push(`gastando como el último año: ${data.band[i][0].toFixed(0)}% a ${data.band[i][1].toFixed(0)}%`);
  return lines.join("\n");
}

// A year as one flow: its monthly-mean income on the left, split into the layers it
// went to on the right, a ribbon joining each pair. The same stack order as the
// columns, savings on top, so a ribbon never crosses another. A year that spent more
// than it earned has the `short` slice too, red on both sides: the bar is then the
// income plus what it ran past it. `scale` is pixels per peso, shared by every
// year so the bands compare; the right side keeps a `gap` between slices.
export const FLOW_ORDER = ["saved", "short", "committed", "other", "undecided", "wants", "needs"];

export function sankey(mean, { scale, width, bar, gap }) {
  const values = {
    saved: Math.max(mean.saved, 0),
    short: Math.max(-mean.saved, 0),
    committed: mean.committed,
    other: mean.other,
    undecided: mean.undecided,
    wants: mean.wants,
    needs: mean.needs,
  };
  const slices = FLOW_ORDER.filter((layer) => values[layer] > 0);
  const total = slices.reduce((sum, layer) => sum + values[layer], 0);
  let left = 0;
  let right = 0;
  const bands = slices.map((layer) => {
    const px = values[layer] * scale;
    const band = { layer, value: values[layer], share: values[layer] / total, from: [left, left + px], to: [right, right + px] };
    left += px;
    right += px + gap;
    const [a1, a2] = band.from;
    const [b1, b2] = band.to;
    const mid = (bar + width - bar) / 2;
    band.path = `M${bar},${a1} C${mid},${a1} ${mid},${b1} ${width - bar},${b1} L${width - bar},${b2} C${mid},${b2} ${mid},${a2} ${bar},${a2} Z`;
    return band;
  });
  return { bands, leftHeight: left, rightHeight: right - gap, total };
}

// The scale every year's flow shares: the tallest year's whole bar fits `height`.
export function flowScale(years, height) {
  const totals = years.map((year) => Math.max(year.mean.income, LAYERS.reduce((sum, layer) => sum + year.mean[layer], 0)));
  return height / Math.max(...totals, 1);
}

// What a peso is worth. The figure arrives in the value of one basket - the household's own,
// or the general IPC when that could not be built - so a month's bar is its nominal pesos
// over that basket's price level (1 at the base month, below 1 before it, above it after).
// The more prices rose, the less a nominal peso is worth and the smaller the bar for the same
// number: the numbers go up with inflation and the bars go down. Past the index there is only
// a range, and the level is its middle.
export function level(data, name, i) {
  const read = data.prices[name][i];
  if (read != null) return { mid: read };
  const band = data.fans[name][i];
  return band ? { mid: (band[0] + band[1]) / 2 } : null;
}

// A figure in the bars' value written as it was in each month's own pesos: times the level
// there. NaN where there is no level, so a number is not drawn wrong.
export const written = (data, values) =>
  values.map((value, i) => {
    const price = level(data, "value", i);
    return value == null ? value : price ? value * price.mid : Number.NaN;
  });

// The same figure measured in the canasta básica's value instead of the bars': written in
// the month's pesos, then over that basket's level. The line the bars are compared with.
export const inCanasta = (data, values) =>
  values.map((value, i) => {
    const [price, basket] = [level(data, "value", i), level(data, "canasta", i)];
    return value == null ? value : price && basket ? (value * price.mid) / basket.mid : Number.NaN;
  });

// What a hover says beside the bar: each month's income and outflow in the pesos of that
// month, and the twelve-month mean outflow in the canasta básica's value.
export function scaled(data) {
  const outflow = data.months.map((_, i) => LAYERS.reduce((sum, layer) => sum + data[layer][i], 0));
  return { ...data, nominal: { income: written(data, data.income), out: written(data, outflow) }, by_canasta: inCanasta(data, data.rolling_out) };
}

// A nominal amount as a line across the months: the height it stands at in the bars'
// value, `N / level`. It is N at the base month, higher before it and lower after, so a
// reader can see how far down inflation takes a round number; ahead of the index it follows
// the middle of the forward range.
export function grid(data, nominal) {
  return data.months.flatMap((_, i) => {
    const basket = level(data, "value", i);
    return basket ? [{ x: i, y: nominal / basket.mid }] : [];
  });
}
