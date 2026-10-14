// Pure tests for `core/scale.js`: no DOM, no dependencies. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { CHART_EM, chartPx } from "../../../src/scaffolding/ui/static/ui/core/scale.js";

test("chartPx turns chart ems into pixels and follows the page's own size", () => {
  assert.equal(CHART_EM, 0.9);
  assert.equal(chartPx(2.4), 35); // one row = 2.4 chart ems at a 16px page
  assert.equal(chartPx(12), 173); // the label column = 12 chart ems
  assert.equal(chartPx(2.4, 20), 43); // a 20px page scales the figures with it
});
