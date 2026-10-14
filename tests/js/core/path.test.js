// Pure tests for `core/path.js`: no DOM. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { named, walk } from "../../../src/scaffolding/ui/static/ui/core/path.js";

const tree = {
  label: "gasto",
  children: [
    { label: "necesito", children: [{ label: "comida", children: [] }] },
    { label: "sin decidir", children: [] },
  ],
};

test("walk follows the labels down", () => {
  assert.deepEqual(named(walk(tree, ["necesito", "comida"])), ["necesito", "comida"]);
  assert.deepEqual(named(walk(tree, [])), []);
});

test("walk stops where the tree no longer has the label", () => {
  assert.deepEqual(named(walk(tree, ["necesito", "viajes", "comida"])), ["necesito"]);
  assert.deepEqual(named(walk(tree, ["quiero"])), []);
});
