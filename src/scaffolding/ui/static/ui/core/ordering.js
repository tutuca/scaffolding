// The order a person is giving a list of things, and what is true of it - as state, with
// the changes to it named for what happened. Browser-free: it knows keys, not rows.
//
// The things are records - `{ key, rank }`, the rank being what was saved ("" for none) -
// in the order the server drew them. The model owns four facts and nothing else owns them:
// the order now, whose it is (the person's, or the plan's), whether it differs from what is
// saved, and which order the derived figures are for (`shown`: the saved one until a what-if
// for another is merged). What to write, what to ask and what is out of date are all derived
// from them.
import { ranks } from "./sort.js";

export function ordering(records) {
  const keys = records.map((record) => record.key);
  const saved = records.map((record) => record.rank);
  const began = keys.join(",");
  const wasMine = saved.some((value) => value !== "");
  let current = [...keys];
  let mine = wasMine;
  let dirty = false;
  let shown = began;

  const ids = () => current.join(",");

  return {
    /** The keys as they stand. */
    get keys() {
      return [...current];
    },
    /** Whether there is something to save. */
    get dirty() {
      return dirty;
    },
    /** Whether what the server derived - dates, the figure - is not for this order: it is the
     * person's and a what-if has not come back, or it is the plan's, which a list of keys
     * cannot ask about. */
    get stale() {
      return dirty && (!mine || ids() !== shown);
    },
    /** What each key's rank input holds: what was saved until the order is changed. */
    get ranks() {
      return dirty ? ranks(current, mine) : [...saved];
    },

    /** The person dropped the things in this order. Back where it began is nothing to save. */
    moved(next) {
      current = [...next];
      if (ids() === began) {
        this.discarded();
        return;
      }
      mine = true;
      dirty = true;
    },
    /** The person gave the order back to the plan: the numbers go, the order on screen stays. */
    leftToPlan() {
      mine = false;
      dirty = true;
    },
    /** The person changed their mind: what was saved, as it was. */
    discarded() {
      current = [...keys];
      mine = wasMine;
      dirty = false;
    },
    /** A what-if for this order came back and its figures are on the page. An empty order is
     * the saved page. */
    shownFor(next) {
      shown = next.length ? next.join(",") : began;
    },
    /** The keys to ask the server about, or null when there is nothing to ask: the person's
     * order that is not the one on screen, or the saved page after the person put it back. */
    asking() {
      if (dirty) return mine && ids() !== shown ? [...current] : null;
      return shown === began ? null : [];
    },
  };
}
