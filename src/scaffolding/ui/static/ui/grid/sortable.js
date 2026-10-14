// The mechanics of moving rows, apart from what a move means.
//
// After Shopify's Draggable (https://shopify.github.io/draggable/): sensors turn what the
// reader does into one small vocabulary - pick up, sort, drop, cancel - and the rest is
// listening. Here the sensors are the pointer (mouse, touch and pen are one thing to
// pointer events; the handle is the only place a drag starts, so the page still scrolls
// under a finger) and the keyboard (Space or Enter picks a row up, the arrows move it,
// Space or Enter drops it, Escape puts it back: the WAI-ARIA pattern, which Draggable
// itself leaves to its plugins).
//
// Like Draggable's mirror, a pointer drag shows a copy of the row that follows the pointer
// while the row itself stays in the list as the place it will land; the list is
// reordered under the pointer as it crosses the middle of a neighbour. Nothing here
// writes a number or asks the server: `render(order)` is told how the rows now stand while
// they are being moved, and `stop(order, before)` is told once, when one is dropped. What
// a drop is worth - a number, a request - is the caller's, and it is paid once per drop.
import { move, slot } from "../core/sort.js";

export function sortable({ host, rows, handleOf, titleOf, render, stop, announce }) {
  let order = [...rows];
  let held = null;

  const put = (row, to) => {
    const from = order.indexOf(row);
    if (from === to || to < 0 || to >= order.length) return false;
    order = move(order, from, to);
    render(order);
    return true;
  };
  const where = (row) => `lugar ${order.indexOf(row) + 1} de ${order.length}`;

  const pick = (row, how) => {
    held = { row, how, before: [...order] };
    row.dataset.dragging = "";
    host.dataset.sorting = "";
    handleOf(row).setAttribute("aria-pressed", "true");
    return held;
  };
  const release = () => {
    const { row } = held;
    delete row.dataset.dragging;
    delete host.dataset.sorting;
    handleOf(row).removeAttribute("aria-pressed");
    const done = held;
    held = null;
    return done;
  };
  const drop = () => {
    const { row, before } = release();
    announce(`${titleOf(row)} soltada: ${where(row)}.`);
    if (order.some((one, index) => one !== before[index])) stop(order, before);
  };
  const cancel = () => {
    const { row, before } = release();
    order = before;
    render(order);
    announce(`${titleOf(row)}: movimiento cancelado.`);
  };

  // The mirror: a copy of the row, taken out of the form (its number input must not
  // post twice) and out of the tab order, laid over the page at the row's own width.
  const mirrorOf = (row) => {
    const box = row.getBoundingClientRect();
    const copy = row.cloneNode(true);
    for (const field of copy.querySelectorAll("input, label")) field.remove();
    copy.inert = true;
    [...row.cells].forEach((cell, index) => {
      copy.cells[index].style.width = `${cell.getBoundingClientRect().width}px`;
    });
    const mirror = document.createElement("table");
    mirror.className = "grid-mirror";
    mirror.setAttribute("aria-hidden", "true");
    mirror.style.width = `${box.width}px`;
    mirror.style.left = `${box.left}px`;
    mirror.append(document.createElement("tbody"));
    mirror.tBodies[0].append(copy);
    // Inside the scroll box, so the table's own rules dress it; `fixed` takes it out of the box.
    row.closest(".table-scroll").append(mirror);
    return { node: mirror, offset: 0, box };
  };

  const dragFrom = (row, handle, event) => {
    if (event.button || handle.disabled || held) return;
    event.preventDefault();
    pick(row, "pointer");
    const mirror = mirrorOf(row);
    const grab = event.clientY - mirror.box.top;
    mirror.node.style.top = `${mirror.box.top}px`;
    announce(`${titleOf(row)} tomada.`);

    const over = (now) => {
      mirror.node.style.top = `${now.clientY - grab}px`;
      const middles = order
        .filter((one) => one !== row)
        .map((one) => {
          const box = one.getBoundingClientRect();
          return box.top + box.height / 2;
        });
      if (put(row, slot(middles, now.clientY))) announce(`${where(row)}.`);
    };
    const end = (finish) => () => {
      removeEventListener("pointermove", over);
      removeEventListener("pointerup", up);
      removeEventListener("pointercancel", abort);
      removeEventListener("keydown", escape);
      mirror.node.remove();
      finish();
    };
    const up = end(drop);
    const abort = end(cancel);
    const escape = (key) => {
      if (key.key === "Escape") abort();
    };
    addEventListener("pointermove", over);
    addEventListener("pointerup", up);
    addEventListener("pointercancel", abort);
    addEventListener("keydown", escape);
  };

  const keyOn = (row, event) => {
    if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      if (held?.row === row) drop();
      else if (!held) {
        pick(row, "keyboard");
        announce(`${titleOf(row)} tomada, ${where(row)}. Flechas para mover, Espacio para soltar, Escape para cancelar.`);
      }
      return;
    }
    if (held?.row !== row) return;
    const step = { ArrowUp: -1, ArrowDown: 1 }[event.key];
    if (step) {
      event.preventDefault();
      if (put(row, order.indexOf(row) + step)) announce(`${where(row)}.`);
      handleOf(row).focus();
    } else if (event.key === "Escape") {
      event.preventDefault();
      cancel();
    }
  };

  for (const row of order) {
    const handle = handleOf(row);
    handle.addEventListener("pointerdown", (event) => dragFrom(row, handle, event));
    handle.addEventListener("keydown", (event) => keyOn(row, event));
    // Leaving a held row where it is keeps the work; it is a drop.
    handle.addEventListener("blur", () => {
      if (held?.row === row && held.how === "keyboard") drop();
    });
  }

  return {
    /** The rows as they stand. */
    get order() {
      return [...order];
    },
    /** The caller put the rows back (a discard): the sensors follow. */
    reset(rowsNow) {
      order = [...rowsNow];
    },
  };
}
