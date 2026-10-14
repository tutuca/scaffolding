// What the table's features compute over rows, browser-free: the order a column
// puts them in. Rows are whatever the caller has (the element passes `<tr>`s) and
// `valueOf` reads the cell. Nothing here mutates its input.

const blank = (value) => value === undefined || value === null || value === "" || value === "—";

const plain = (text) =>
  String(text)
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();

/** Whether `text` has every word of `query`, in any order, ignoring case and accents:
 * what a person means by typing "prestamo" at "Préstamo Galicia". An empty query
 * matches everything. */
export const matches = (text, query) => {
  const haystack = plain(text);
  return plain(query)
    .split(/\s+/)
    .filter(Boolean)
    .every((word) => haystack.includes(word));
};

/** The direction after this one: none, ascending, descending, none. */
export const nextDirection = (current) => (current ? (current === "ascending" ? "descending" : undefined) : "ascending");

/** `items` ordered by `valueOf(item)`. A cell with nothing in it goes last in either
 * direction (it has no place to rank), and equal values keep the order they came in. */
export function sorted(items, valueOf, type, direction) {
  const sign = direction === "descending" ? -1 : 1;
  const keyed = items.map((item, index) => ({ item, index, value: valueOf(item) }));
  keyed.sort((a, b) => {
    const empty = [blank(a.value), blank(b.value)];
    if (empty[0] || empty[1]) return empty[0] === empty[1] ? a.index - b.index : empty[0] ? 1 : -1;
    const order =
      type === "number" ? Number(a.value) - Number(b.value) : String(a.value).localeCompare(String(b.value), "es");
    return order * sign || a.index - b.index;
  });
  return keyed.map((one) => one.item);
}
