// Pure tests for `core/bars.js`: no DOM, no dependencies. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { flowBars, paretoBars } from "../../../src/scaffolding/ui/static/ui/core/bars.js";

test("paretoBars normalizes the tallest bar to 100 and carries the cumulative", () => {
  const rows = [
    { label: "super", value: 900, bucket: "needs", caption: "900" },
    { label: "kiosco", value: 100, bucket: "wants", caption: "100" },
  ];

  const { max, bars, points } = paretoBars(rows, [90, 100]);

  assert.equal(max, 900);
  assert.equal(bars[0].width, 100);
  assert.equal(bars[1].width, (100 / 900) * 100);
  assert.deepEqual(points, [
    { y: "super", cum: 90 },
    { y: "kiosco", cum: 100 },
  ]);
});

test("flowBars reshapes each month into an ingresos and an egresos bar", () => {
  const bars = flowBars(["2026-08", "2026-09"], [9000, 9500], [8000, 7000], ["9,000", "9,500"], ["8,000", "7,000"]);

  assert.deepEqual(bars, [
    { x1: -0.38, x2: 0, labelX: -0.19, y: 9000, caption: "9,000", series: "ingresos" },
    { x1: 0, x2: 0.38, labelX: 0.19, y: 8000, caption: "8,000", series: "egresos" },
    { x1: 0.62, x2: 1, labelX: 0.81, y: 9500, caption: "9,500", series: "ingresos" },
    { x1: 1, x2: 1.38, labelX: 1.19, y: 7000, caption: "7,000", series: "egresos" },
  ]);
});
