// The `sort` feature: a header that has `data-sort` becomes a button that orders the
// rows by that column - ascending, descending, back to the natural order. Without
// this script the headers are text and the rows are the server's order.
//
// A cell's value is its `data-value` when the server wrote one (money is shown as
// "3.0 M" and sorts as 3000000) and its text otherwise.
import { nextDirection, sorted } from "../core/rows.js";

export default function sort(host) {
  let current;

  for (const column of host.columns.filter((one) => one.type)) {
    const button = document.createElement("button");
    button.type = "button";
    button.append(...column.th.childNodes);
    button.addEventListener("click", () => {
      const direction = nextDirection(current?.key === column.key ? current.direction : undefined);
      current = direction && { key: column.key, direction };
      host.refresh();
    });
    column.th.append(button);
  }

  const column = () => host.columns.find((one) => one.key === current?.key);

  return {
    name: "sort",
    stage(rows) {
      // The mark is set here, before the draw, so a feature that refreshes after it
      // (the handles of `reorder`) reads the sort that was just applied.
      host.toggleAttribute("data-sorted", Boolean(current));
      const by = column();
      if (!by) return rows;
      const valueOf = (row) => row.cells[by.index].dataset.value ?? row.cells[by.index].textContent.trim();
      return sorted(rows, valueOf, by.type, current.direction);
    },
    refresh() {
      for (const one of host.columns.filter((other) => other.type)) {
        if (one.key === current?.key) one.th.setAttribute("aria-sort", current.direction);
        else one.th.removeAttribute("aria-sort");
      }
    },
    get state() {
      return current;
    },
    set state(value) {
      current = value;
    },
  };
}
