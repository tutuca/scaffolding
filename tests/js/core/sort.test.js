// Pure tests for `core/sort.js`: no DOM. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { move, ranks, slot } from "../../../src/scaffolding/ui/static/ui/core/sort.js";

test("move takes an item out and puts it back, leaving the input alone", () => {
  const order = ["a", "b", "c", "d"];

  assert.deepEqual(move(order, 0, 2), ["b", "c", "a", "d"]);
  assert.deepEqual(move(order, 3, 0), ["d", "a", "b", "c"]);
  assert.deepEqual(move(order, 1, 1), order);
  assert.deepEqual(order, ["a", "b", "c", "d"]);
});

test("slot counts the midpoints the pointer has passed", () => {
  const middles = [10, 30, 50];

  assert.equal(slot(middles, 0), 0);
  assert.equal(slot(middles, 31), 2);
  assert.equal(slot(middles, 500), 3);
  assert.equal(slot([], 5), 0);
});

test("ranks are the places when the order is the person's, and empty when the plan decides", () => {
  assert.deepEqual(ranks(["a", "b", "c"], true), ["1", "2", "3"]);
  assert.deepEqual(ranks(["a", "b", "c"], false), ["", "", ""]);
});
