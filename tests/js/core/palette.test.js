// Pure tests for `core/palette.js`: no DOM, no dependencies. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { BUCKET_TOKENS, colorToken, turned } from "../../../src/scaffolding/ui/static/ui/core/palette.js";

test("colorToken maps each bucket to its chart token", () => {
  assert.equal(colorToken("needs"), "--chart-needs");
  assert.equal(colorToken("wants"), "--chart-wants");
  assert.equal(colorToken("structural"), "--chart-structural");
  assert.equal(colorToken("income"), "--chart-income");
  assert.equal(colorToken("sin decidir"), "--chart-undecided");
});

test("the savings green is the income green, not the brand fallback", () => {
  assert.equal(colorToken("ahorro"), "--chart-income");
});

test("colorToken maps the ink names and the accent to their tokens", () => {
  assert.equal(colorToken("ink"), "--ink");
  assert.equal(colorToken("muted"), "--ink-quiet");
  assert.equal(colorToken("band"), "--line");
  assert.equal(colorToken("white"), "#fff");
  assert.equal(colorToken("accent"), "--chart-undecided");
});

test("an unknown color name falls back to the brand, not an error", () => {
  assert.equal(colorToken("no-such-bucket"), "--brand");
});

test("every bucket resolves to a chart token, never the brand fallback", () => {
  for (const name of Object.keys(BUCKET_TOKENS)) {
    assert.notEqual(colorToken(name), "--brand", `${name} fell through to --brand`);
  }
});

test("turned leaves a color alone with no turn, and rotates a hue by a triad or a complement", () => {
  assert.equal(turned("#4c72b0"), "#4c72b0");
  assert.equal(turned("#4c72b0", { hue: 120 }), "#b04c72");
  assert.equal(turned("#4c72b0", { hue: 180 }), "#b08a4c");
  assert.equal(turned("#4c72b0", { hue: -240 }), turned("#4c72b0", { hue: 120 }));
});

test("turned clamps saturation and lightness, and a gray stays a gray", () => {
  assert.equal(turned("#9a9a9a", { hue: 120 }), "#9a9a9a");
  assert.equal(turned("#4c72b0", { light: 1 }), "#ffffff");
  assert.equal(turned("#4c72b0", { sat: 0 }), turned("#4c72b0", { sat: 0, hue: 90 }));
});

test("turned round-trips a color whichever channel is largest, and across every hue sextant", () => {
  for (const hex of ["#dd8452", "#55a868", "#4c72b0", "#c44e52", "#a85595", "#6855a8"]) assert.equal(turned(hex), hex);
  for (let hue = 0; hue < 360; hue += 30) assert.match(turned("#dd8452", { hue }), /^#[0-9a-f]{6}$/);
});
