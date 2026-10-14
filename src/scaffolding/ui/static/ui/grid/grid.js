// `<data-grid>`: the table primitive with every feature on it. Which of them a given
// grid uses is written in its markup, not in an attribute: a header with `data-sort`
// sorts, a search box with `data-filter` filters, a row with a `rank_<id>` input
// moves. A feature whose markup is absent does nothing.
//
// The order here is the order of the stages; none depends on another today.
import { DataTable } from "../table/table.js";

class DataGrid extends DataTable {
  static features = {
    sort: () => import("./sort.js"),
    filter: () => import("./filter.js"),
    reorder: () => import("./reorder.js"),
  };
}

customElements.define("data-grid", DataGrid);
