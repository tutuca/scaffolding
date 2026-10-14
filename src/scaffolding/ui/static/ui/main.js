// The one script a page loads: the entrypoint that brings up the chart and
// telescope world only when the page has figures to draw.
//
// The vendored d3 and Plot are UMD globals - Plot's factory reads `window.d3`,
// so the two are injected in that order and awaited - and only then are the
// renderers imported with a dynamic `import()`. No build; a page with no
// figures (login, colophon, certificado) downloads none of it. `telescope.js`
// registers `<spending-telescope>` as a side effect, which upgrades the
// elements already in the document.
import "./nav.js";
import "./swap.js";

const vendor = (file) => new URL(`./vendor/${file}`, import.meta.url).href;

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = src;
    script.onload = resolve;
    script.onerror = reject;
    document.head.append(script);
  });
}

async function init() {
  if (document.querySelector("[data-live]")) await import("./components/form/form.js");
  if (document.querySelector("data-table")) await import("./table/table.js");
  if (document.querySelector("data-grid")) await import("./grid/grid.js");
  const figures = document.querySelectorAll("[data-chart]");
  const telescope = document.querySelector("spending-telescope");
  if (!figures.length && !telescope) return;

  await loadScript(vendor("d3.min.js"));
  await loadScript(vendor("plot.umd.min.js"));

  if (telescope) await import("./telescope.js");
  if (figures.length) {
    const { mount } = await import("./charts/mount.js");
    await mount();
  }
}

init();
