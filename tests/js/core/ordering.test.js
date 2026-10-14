// Pure tests for `core/ordering.js`: no DOM. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { ordering } from "../../../src/scaffolding/ui/static/ui/core/ordering.js";

const KEYS = ["3", "4", "1", "2"];
const NONE = ["", "", "", ""];
const fresh = (saved = NONE) => ordering(KEYS.map((key, index) => ({ key, rank: saved[index] })));

test("a fresh order is what was saved: nothing to write, ask or doubt", () => {
  const model = fresh(["1", "", "3", ""]);

  assert.deepEqual(model.keys, KEYS);
  assert.deepEqual(model.ranks, ["1", "", "3", ""]);
  assert.equal(model.dirty, false);
  assert.equal(model.stale, false);
  assert.equal(model.asking(), null);
});

test("a move is the person's order: numbered, unsaved, stale until its what-if is shown", () => {
  const model = fresh();

  model.moved(["4", "1", "3", "2"]);

  assert.deepEqual(model.keys, ["4", "1", "3", "2"]);
  assert.deepEqual(model.ranks, ["1", "2", "3", "4"]);
  assert.equal(model.dirty, true);
  assert.equal(model.stale, true);
  assert.deepEqual(model.asking(), ["4", "1", "3", "2"]);

  model.shownFor(["4", "1", "3", "2"]);

  assert.equal(model.stale, false);
  assert.equal(model.asking(), null);
});

test("an order that is already the one on screen asks nothing", () => {
  const model = fresh();
  model.moved(["4", "1", "3", "2"]);
  model.shownFor(["4", "1", "3", "2"]);

  model.moved(["1", "4", "3", "2"]);
  assert.deepEqual(model.asking(), ["1", "4", "3", "2"]);

  model.moved(["4", "1", "3", "2"]);
  assert.equal(model.asking(), null);
  assert.equal(model.stale, false);
});

test("an order moved back to where it began is not a change, and the saved page comes back if it was replaced", () => {
  const model = fresh(["1", "", "3", ""]);
  model.moved(["4", "1", "3", "2"]);
  model.shownFor(["4", "1", "3", "2"]);

  model.moved(KEYS);

  assert.equal(model.dirty, false);
  assert.deepEqual(model.ranks, ["1", "", "3", ""]);
  assert.deepEqual(model.asking(), []);

  model.shownFor([]);

  assert.equal(model.asking(), null);
});

test("moved back before anything was asked is nothing at all", () => {
  const model = fresh();
  model.moved(["4", "1", "3", "2"]);

  model.moved(KEYS);

  assert.equal(model.dirty, false);
  assert.equal(model.asking(), null);
});

test("giving the order to the plan blanks the numbers, keeps the rows where they are, and cannot be asked about", () => {
  const model = fresh(["1", "2", "3", "4"]);

  model.leftToPlan();

  assert.deepEqual(model.keys, KEYS);
  assert.deepEqual(model.ranks, NONE);
  assert.equal(model.dirty, true);
  assert.equal(model.stale, true);
  assert.equal(model.asking(), null);
});

test("discarding puts back the order, whose it was and the numbers saved", () => {
  const model = fresh(["1", "", "3", ""]);
  model.moved(["4", "1", "3", "2"]);
  model.leftToPlan();

  model.discarded();

  assert.deepEqual(model.keys, KEYS);
  assert.deepEqual(model.ranks, ["1", "", "3", ""]);
  assert.equal(model.dirty, false);
  assert.equal(model.stale, false);
});

test("a person's order after the plan's is numbered again", () => {
  const model = fresh(["1", "2", "3", "4"]);
  model.leftToPlan();

  model.moved(["4", "1", "3", "2"]);

  assert.deepEqual(model.ranks, ["1", "2", "3", "4"]);
});

test("keys come out as copies: the model owns them", () => {
  const model = fresh();

  model.keys.push("9");
  model.ranks.push("9");

  assert.deepEqual(model.keys, KEYS);
  assert.deepEqual(model.ranks, NONE);
});
