// The one script a page loads: the entrypoint that brings up a component's
// interactivity only when the page uses it. No build, no vendored libraries.
import "./nav.js";

async function init() {
  if (document.querySelector("[data-live]")) await import("./components/form/form.js");
  if (document.querySelector("data-table")) await import("./table/table.js");
  if (document.querySelector("data-grid")) await import("./grid/grid.js");
}

init();
