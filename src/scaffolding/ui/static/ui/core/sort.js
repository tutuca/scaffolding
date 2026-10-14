// The arithmetic of a sortable list, browser-free: where a row goes, and the
// numbers the order is written down as. The element (`sortable.js`) owns the DOM.

/** `order` with the item at `from` taken out and put back at `to`. */
export function move(order, from, to) {
  const next = [...order];
  next.splice(to, 0, ...next.splice(from, 1));
  return next;
}

/** Which place a pointer at `y` is over: how many row midpoints it has passed. */
export const slot = (midpoints, y) => midpoints.filter((middle) => y > middle).length;

/** What each item in `order` is stored as: its place, or nothing when the plan
 * decides the order. */
export const ranks = (order, mine) => order.map((_, index) => (mine ? String(index + 1) : ""));
