// The `filter` feature: the search box inside the table (`input[data-filter]`) narrows
// the rows on this page as the reader types. Without this script the box is the
// form's: Enter searches every row the server has, which is the real search - this
// only saves a round trip for the rows already here.
//
// Nothing is filtered until the reader types: the box opens with the server's own
// search in it, and the page already is that search.
import { matches } from "../core/rows.js";

// What a row says: the text of its cells, leaving out the ones that hold a control - the
// options of a dropdown are the whole vocabulary, not what the row is about.
const said = new WeakMap();
const textOf = (row) => {
  if (!said.has(row)) {
    said.set(row, [...row.cells].map((cell) => (cell.querySelector("select, input, textarea") ? "" : cell.textContent)).join(" "));
  }
  return said.get(row);
};

export default function filter(host) {
  const input = host.querySelector("input[data-filter]");
  if (!input) return { name: "filter" };
  let typed = false;
  const live = document.createElement("p");
  live.className = "quiet";
  live.setAttribute("aria-live", "polite");
  input.closest("form").after(live);
  input.addEventListener("input", () => {
    typed = true;
    host.refresh();
  });

  return {
    name: "filter",
    stage(rows) {
      return typed ? rows.filter((row) => matches(textOf(row), input.value)) : rows;
    },
    refresh() {
      const all = host.natural.length;
      const shown = host.natural.filter((row) => !row.hidden).length;
      live.textContent = typed && shown !== all ? `${shown} de ${all} en esta página.` : "";
    },
  };
}
