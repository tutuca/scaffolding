// Pure tests for `core/trajectory.js`: no DOM, no dependencies. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { columns, crest, describe, flowScale, grid, inCanasta, level, padded, sankey, scaled, written, quarterTicks, seamed, tickLabel, yearSeams } from "../../../src/scaffolding/ui/static/ui/core/trajectory.js";

const data = {
  seen: 1,
  months: ["2026-12", "2027-01"],
  income: [100, 80],
  needs: [40, 50],
  wants: [20, 30],
  undecided: [0, 10],
  committed: [10, 10],
  other: [0, 0],
  saved: [30, -20],
};

test("a month that kept money stacks its layers and fills the margin up to the income", () => {
  const rects = columns(data).filter((r) => r.i === 0);
  assert.deepEqual(rects.map((r) => [r.layer, r.y1, r.y2]), [["needs", 0, 40], ["wants", 40, 60], ["committed", 60, 70], ["saved", 70, 100]]);
});

test("a month that overspent draws the overshoot above its income, and the zero layer is left out", () => {
  const rects = columns(data).filter((r) => r.i === 1);
  assert.deepEqual(rects.at(-1), { i: 1, period: "2027-01", observed: false, layer: "short", y1: 80, y2: 100 });
  assert.equal(rects.length, 5);
  assert.equal(crest(data), 100);
});

test("ticks start each quarter, the year seams fall between December and January", () => {
  const months = ["2026-11", "2026-12", "2027-01", "2027-02", "2027-04"];
  assert.deepEqual(quarterTicks(months), [2, 4]);
  assert.deepEqual(quarterTicks(months, 6), [2]);
  assert.deepEqual(yearSeams(months), [1.5]);
  assert.equal(tickLabel("2027-01"), "ene 27");
  assert.equal(tickLabel("2027-04"), "abr");
});

test("a seamed line meets itself at the last observed point and skips the gaps", () => {
  const { observed, planned } = seamed([null, 1, 2, 3], 3);
  assert.deepEqual(observed.map((p) => p.x), [1, 2]);
  assert.deepEqual(planned.map((p) => p.x), [2, 3]);
});

test("a scale is padded by a fraction of its own span, and a flat one still gets room", () => {
  assert.deepEqual(padded([0, 100], 0.1), [-10, 110]);
  assert.deepEqual(padded([5, 5], 0.5), [4.5, 5.5]);
});

test("a hover names the month, its kind and the band only where there is one", () => {
  const full = {
    ...data,
    needs: [4e6, 5e6],
    wants: [2e6, 3e6],
    undecided: [0, 1e6],
    committed: [1e6, 1e6],
    income: [10e6, 8e6],
    saved: [3e6, -2e6],
    rate: [30, -25],
    cumulative: [3e6, 1e6],
    band: [null, [-20, 10]],
  };

  assert.match(describe(full, 0), /^2026-12 · observado\ningreso 10.0 M/);
  assert.doesNotMatch(describe(full, 0), /último año/);
  assert.match(describe(full, 1), /proyectado[\s\S]*ahorro -2.0 M \(-25%\)[\s\S]*-20% a 10%/);
});

test("a year's flow slices its mean by layer, shares one scale, and a ribbon joins each pair", () => {
  const mean = { income: 100, needs: 40, wants: 20, undecided: 0, committed: 10, other: 0, saved: 30 };
  const flow = sankey(mean, { scale: 2, width: 200, bar: 8, gap: 5 });

  assert.deepEqual(flow.bands.map((b) => b.layer), ["saved", "committed", "wants", "needs"]);
  assert.deepEqual(flow.bands[0].from, [0, 60]);
  assert.deepEqual(flow.bands[0].to, [0, 60]);
  assert.deepEqual(flow.bands[1].to, [65, 85]);
  assert.equal(flow.leftHeight, 200);
  assert.equal(flow.rightHeight, 215);
  assert.equal(flow.total, 100);
  assert.match(flow.bands[0].path, /^M8,0 C100,0 100,0 192,0 L192,60 C100,60 100,60 8,60 Z$/);
});

test("a year that spent past its income gets a short slice, and the scale fits the tallest year", () => {
  const over = { income: 80, needs: 60, wants: 30, undecided: 0, committed: 10, other: 0, saved: -20 };
  const flow = sankey(over, { scale: 1, width: 100, bar: 4, gap: 0 });
  assert.deepEqual(flow.bands.map((b) => b.layer), ["short", "committed", "wants", "needs"]);
  assert.equal(flow.total, 120);

  const years = [{ mean: over }, { mean: { income: 200, needs: 1, wants: 1, undecided: 1, committed: 1, other: 0, saved: 196 } }];
  assert.equal(flowScale(years, 100), 0.5);
});

// Three months: two observed (the second is the base, worth 1), one ahead with a range. The
// bars' basket stands at 0.8, 1, then 1.1 ahead; the canasta básica at 0.9, 1, then 1.05.
const priced = {
  ...data,
  seen: 2,
  months: ["2026-11", "2026-12", "2027-01"],
  income: [100, 100, 100],
  needs: [40, 40, 40],
  wants: [20, 20, 20],
  undecided: [0, 0, 0],
  committed: [10, 10, 10],
  other: [0, 0, 0],
  saved: [30, 30, 30],
  rolling_out: [null, 70, 70],
  cumulative: [30, 60, 80],
  canasta: 10,
  prices: { value: [0.8, 1, null], canasta: [0.9, 1, null] },
  fans: { value: [null, null, [1, 1.2]], canasta: [null, null, [1, 1.1]] },
};

test("a level is the reading, or the middle of the range a month ahead can have", () => {
  assert.deepEqual(level(priced, "value", 0), { mid: 0.8 });
  assert.ok(Math.abs(level(priced, "value", 2).mid - 1.1) < 1e-12);
  assert.equal(level({ ...priced, fans: { ...priced.fans, value: [null, null, null] } }, "value", 2), null);
});

test("a figure is written in each month's pesos by the level there: smaller before the base, larger after", () => {
  const out = written(priced, [100, null, 100]);

  assert.ok(Math.abs(out[0] - 80) < 1e-9 && out[1] === null && Math.abs(out[2] - 110) < 1e-9);
  assert.ok(Number.isNaN(written({ ...priced, fans: { ...priced.fans, value: [null, null, null] } }, [1, 1, 1])[2]));
});

test("a figure in the canasta básica's value is its nominal over that basket's level", () => {
  const line = inCanasta(priced, [70, 70, null]);

  assert.ok(Math.abs(line[0] - (70 * 0.8) / 0.9) < 1e-9);
  assert.equal(line[1], 70);
  assert.equal(line[2], null);
  assert.ok(Number.isNaN(inCanasta({ ...priced, fans: { ...priced.fans, canasta: [null, null, null] } }, [1, 1, 1])[2]));
});

test("a scaled figure keeps what each month was written in and the mean in the canasta's value", () => {
  const view = scaled(priced);

  assert.ok(Math.abs(view.nominal.income[0] - 80) < 1e-9);
  assert.ok(Math.abs(view.nominal.out[0] - 56) < 1e-9);
  assert.ok(Math.abs(view.by_canasta[2] - (70 * 1.1) / 1.05) < 1e-9);
  assert.equal(view.by_canasta[0], null);
  assert.deepEqual(view.income, priced.income);
});

test("a nominal amount stands at N over the level: higher before the base, lower after", () => {
  const line = grid(priced, 10);

  assert.ok(Math.abs(line[0].y - 10 / 0.8) < 1e-9);
  assert.equal(line[1].y, 10);
  assert.ok(Math.abs(line[2].y - 10 / 1.1) < 1e-9);
  assert.deepEqual(grid({ ...priced, fans: { ...priced.fans, value: [null, null, null] } }, 10).map((d) => d.x), [0, 1]);
});

test("a hover says what the month was written in beside what it is worth", () => {
  const hover = describe({ ...scaled(priced), band: [null, null, null], rate: [30, 30, 30] }, 0);

  assert.match(hover, /en pesos del mes: ingreso 0\.0 M · gasto 0\.0 M/);
  assert.doesNotMatch(describe({ ...priced, band: [null, null, null], rate: [30, 30, 30] }, 0), /en pesos del mes/);
});

test("cash and fees sit above what was chosen and under what was committed", () => {
  const traced = { ...data, other: [5, 0], saved: [25, -20] };
  const rects = columns(traced).filter((r) => r.i === 0);

  assert.deepEqual(rects.map((r) => [r.layer, r.y1, r.y2]), [
    ["needs", 0, 40],
    ["wants", 40, 60],
    ["other", 60, 65],
    ["committed", 65, 75],
    ["saved", 75, 100],
  ]);
});
