// `<data-table>`: the table as a primitive, and the base of the grid.
//
// It wraps a table the server rendered and leaves its markup alone. What it adds is the
// model every feature needs and a seam for them: the columns, read from the headers
// (`data-key`, and whatever else a feature wants a header to say, such as `data-sort`
// or `data-derived`); the rows, from the body (`data-key` is the row's key); the natural
// order, which is the server's until a feature that moves rows writes it
// (`host.natural = rows`); and a draw (`refresh`) that runs the features' stages over
// the natural order. A bare `<data-table>` has no features and is a table with a name.
// `static features` is the extension point: a subclass lists its features, in order, as
// name -> loader (`<data-grid>`, in `../grid/`, is the full set).
//
// A feature is a function `(host) => { name, stage?, refresh?, state }`:
//   - `stage(rows)` returns the rows as that feature would show them; the stages run in
//     order over the natural order and the result is what the body holds;
//   - `refresh()` runs after the body is drawn;
//   - `state` is whatever the feature keeps that a swap of the page should carry across
//     (the element is `data-keep`; the state is held until the features have loaded).
// A feature finds its own markup and does nothing when it is not there, and every one
// has a version that works without any script (a number input, a link, a form).
// Light DOM, so the page's stylesheet dresses everything.
export class DataTable extends HTMLElement {
  // The extension point: an ordered table of feature name -> loader. The primitive has
  // none; `<data-grid>` is this class with the full set, and anything that wants its
  // own set subclasses it the same way.
  static features = {};

  #natural = [];
  #features = [];
  // The features load asynchronously, and a swap hands the state over the moment the
  // element is in the page: it is kept until there is a feature to give it to.
  #wanted;
  #ready = false;

  async connectedCallback() {
    this.table = this.querySelector("table");
    this.body = this.table.tBodies[0];
    this.columns = [...this.table.tHead.rows[0].cells].map((th, index) => ({
      th,
      index,
      key: th.dataset.key ?? String(index),
      type: th.dataset.sort,
      derived: "derived" in th.dataset,
    }));
    this.#natural = [...this.body.rows];
    for (const row of this.#natural) {
      for (const column of this.columns.filter((one) => one.derived)) row.cells[column.index].dataset.derived = "";
    }
    const modules = await Promise.all(Object.values(this.constructor.features).map((load) => load()));
    this.#features = modules.map((module) => module.default(this));
    this.#ready = true;
    this.#apply();
    this.refresh();
  }

  #apply() {
    if (!this.#wanted) return;
    for (const feature of this.#features) if (feature.name in this.#wanted) feature.state = this.#wanted[feature.name];
    this.#wanted = undefined;
  }

  get natural() {
    return [...this.#natural];
  }

  set natural(rows) {
    this.#natural = [...rows];
    this.refresh();
  }

  refresh() {
    const shown = this.#features.reduce((rows, feature) => feature.stage?.(rows) ?? rows, this.#natural);
    this.body.append(...shown);
    // A row no stage kept is hidden, not removed: the natural order still holds it.
    const kept = new Set(shown);
    for (const row of this.#natural) row.hidden = !kept.has(row);
    for (const feature of this.#features) feature.refresh?.();
  }

  get state() {
    return Object.fromEntries(
      this.#features.filter((feature) => feature.state !== undefined).map((feature) => [feature.name, feature.state]),
    );
  }

  set state(state) {
    this.#wanted = state;
    if (!this.#ready) return;
    this.#apply();
    this.refresh();
  }
}

customElements.define("data-table", DataTable);
