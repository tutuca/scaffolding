// Pure tests for `core/rows.js`: no DOM. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { matches, nextDirection, sorted } from "../../../src/scaffolding/ui/static/ui/core/rows.js";

const value = (row) => row.v;
const rows = (...values) => values.map((v, id) => ({ id, v }));
const ids = (list) => list.map((row) => row.id);

test("a query matches when every word is in the text, whatever the case or the accents", () => {
  assert.equal(matches("Préstamo Galicia · 2026-11", "prestamo galicia"), true);
  assert.equal(matches("Préstamo Galicia", "galicia PRÉSTAMO"), true);
  assert.equal(matches("Préstamo Galicia", "nacion"), false);
  assert.equal(matches("Préstamo Galicia", "galicia nacion"), false);
  assert.equal(matches("anything", "   "), true);
  assert.equal(matches("anything", ""), true);
});

test("a header cycles ascending, descending, none", () => {
  assert.equal(nextDirection(undefined), "ascending");
  assert.equal(nextDirection("ascending"), "descending");
  assert.equal(nextDirection("descending"), undefined);
});

test("numbers sort as numbers, not as the text they were written as", () => {
  const list = rows("9", "10", "2");

  assert.deepEqual(ids(sorted(list, value, "number", "ascending")), [2, 0, 1]);
  assert.deepEqual(ids(sorted(list, value, "number", "descending")), [1, 0, 2]);
});

test("text sorts by the reader's alphabet", () => {
  const list = rows("pagar el préstamo familiar", "arreglar el auto", "Cancelar el préstamo", "árbol");

  assert.deepEqual(ids(sorted(list, value, "text", "ascending")), [3, 1, 2, 0]);
});

test("an empty cell goes last whichever way, and ties keep their order", () => {
  const list = rows("b", "—", "a", "", "b", undefined);

  assert.deepEqual(ids(sorted(list, value, "text", "ascending")), [2, 0, 4, 1, 3, 5]);
  assert.deepEqual(ids(sorted(list, value, "text", "descending")), [0, 4, 2, 1, 3, 5]);
});

test("sorting leaves its input alone", () => {
  const list = rows("b", "a");

  sorted(list, value, "text", "ascending");

  assert.deepEqual(ids(list), [0, 1]);
});
