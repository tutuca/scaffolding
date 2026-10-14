// The `reorder` feature: the rows that carry a rank input - `input[name^="rank_"]`, tied
// to a form - are moved by dragging a handle or from the keyboard (`sortable.js`), and the
// numbers are written into the inputs. Without this script the inputs are in the cells and
// the form in the table's actions posts them, which is the whole feature.
//
// The order is a model (`../core/ordering.js`): its state, and what is true of it, live
// there and nowhere else. This file is the shell around it: the sensors tell the model what
// the person did (`moved`, `leftToPlan`, `discarded`), and `render` draws the page from the
// model - the rows, the numbers, the table actions, what is stale - and `settle` asks the
// server what the page would say for an order that is not the one on screen
// (`../preview.js`): once per change, after a short wait, abortable.
//
// The handles, the order's buttons and its note are in the markup, hidden: the server drew
// them and this script only shows what works. A refused order comes back with its numbers
// wrong and visible, and the plain inputs stay so they can be fixed. While the grid is
// sorted by a column the handles are off: a row has no place in an order that is not its own.
import { ordering } from "../core/ordering.js";
import { cancelPreview, preview } from "../preview.js";
import { sortable } from "./sortable.js";

// How long after a change before the page is asked: a second change inside it is one ask.
const WAIT = 300;

export default function reorder(host) {
  const movable = host.natural.filter((row) => row.querySelector('input[name^="rank_"]'));
  const form = movable[0]?.querySelector("input").form;
  if (!form || host.querySelector("[aria-invalid]")) return { name: "reorder" };

  const inputOf = (row) => row.querySelector('input[name^="rank_"]');
  const handleOf = (row) => row.querySelector("[data-handle]");
  // The markup is read once, into records; from here on the model and the rows meet by key.
  const records = movable.map((row) => ({ key: row.dataset.key, title: row.dataset.title, rank: inputOf(row).value }));
  const rowOf = new Map(movable.map((row, index) => [records[index].key, row]));
  const keyOf = new Map(movable.map((row, index) => [row, records[index].key]));
  const titleOf = new Map(records.map((record) => [record.key, record.title]));
  const model = ordering(records);

  const slots = host.natural.map((row, index) => (movable.includes(row) ? index : -1)).filter((index) => index >= 0);
  const place = (rows) => {
    const next = host.natural;
    slots.forEach((at, index) => {
      next[at] = rows[index];
    });
    host.natural = next;
  };

  const live = document.createElement("p");
  live.className = "visually-hidden";
  live.setAttribute("aria-live", "polite");
  host.append(live);
  const announce = (text) => {
    live.textContent = text;
  };

  const part = (name) => form.querySelector(`[data-action="${name}"]`);
  const [discard, plan] = ["discard", "plan"].map(part);
  const note = form.querySelector("[data-note]");
  form.querySelector("[data-baseline]").hidden = true;
  note.hidden = false;
  discard.hidden = false;
  plan.hidden = false;

  // The page, drawn from the model.
  const render = () => {
    const rows = model.keys.map((key) => rowOf.get(key));
    if (rows.some((row, index) => row !== host.natural[slots[index]])) place(rows);
    sorter.reset(rows);
    rows.forEach((row, index) => {
      inputOf(row).value = model.ranks[index];
    });
    form.hidden = !model.dirty;
    host.toggleAttribute("data-stale", model.stale);
    // Short, so the bar fits the row it appears in and the table does not move under the reader's hand.
    note.textContent = model.stale ? "Sin guardar · fechas por recalcular" : "Sin guardar";
  };

  // Asking is the shell's, because it waits and aborts; what to ask is the model's.
  let waiting;
  const settle = () => {
    clearTimeout(waiting);
    cancelPreview();
    const wanted = model.asking();
    if (!wanted) return;
    waiting = setTimeout(async () => {
      if ((await preview(host, wanted)) !== "merged") return;
      model.shownFor(wanted);
      render();
    }, WAIT);
  };

  const sorter = sortable({
    host,
    rows: movable,
    handleOf,
    titleOf: (row) => titleOf.get(keyOf.get(row)),
    render: place,
    announce,
    stop(rows) {
      model.moved(rows.map((row) => keyOf.get(row)));
      render();
      settle();
    },
  });

  for (const row of movable) {
    inputOf(row).hidden = true;
    for (const label of row.querySelectorAll("label")) label.hidden = true;
    handleOf(row).hidden = false;
  }

  discard.addEventListener("click", () => {
    model.discarded();
    render();
    settle();
    announce("Orden descartado.");
  });
  plan.addEventListener("click", () => {
    model.leftToPlan();
    render();
    settle();
    announce("El plan decide el orden.");
  });
  render();

  return {
    name: "reorder",
    refresh() {
      for (const handle of host.querySelectorAll("[data-handle]")) {
        handle.disabled = host.hasAttribute("data-sorted");
        handle.title = handle.disabled
          ? "Quitá el orden por columna para mover filas"
          : "Arrastrala, o Espacio y las flechas";
      }
    },
  };
}
