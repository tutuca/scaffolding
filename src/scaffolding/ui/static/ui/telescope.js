// The telescope: a charting primitive, as a custom element.
//
// One level of a tree at a time - click a bar to enter, the breadcrumb to back
// out. A tree whose nodes carry `previous_month`/`last_month` renders three
// stacked full-width charts (the year, the month before last, the last month);
// otherwise one chart. Within a level the largest item is full-strength and
// each smaller one reads lighter, so the members of a category are told apart
// at a glance; hue stays put, only lightness moves. Plot draws the bars; the
// data is the JSON the view embeds in the `<script id>` the `source` attribute
// names. Vanilla on purpose: two vendored scripts (d3, plot) and this module,
// no build.
import { fitLabels, unlabel } from "./charts/base.js";
import { named, walk } from "./core/path.js";
import { CHART_EM, chartPx } from "./core/scale.js";
import { color, css, money, spines, textMargin } from "./tokens.js";

// The same chart scale as `charts/mount.js`: the base font is `CHART_EM` (0.9em,
// `core/scale.js`) and the px measures are multiples of it, read from the
// reader's own size.
const pagePx = () => parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
const BASE_FONT = `${CHART_EM}em`;
const ROW = () => chartPx(1.6, pagePx()); // the telescope is denser: 1.6 chart ems a row
const LABEL = () => chartPx(12, pagePx());

// A leaf level is one row per capped description; "sin decidir" runs into the
// hundreds and a bar chart that tall is unreadable. Show the largest, note the
// rest.
const LEAF_ROWS = 30;

// Lightness only - hue stays put. d3 does the hex→rgb and back; Plot already
// depends on the vendored d3, so this rides the same global.
const lighten = (hex, t) => {
  const c = d3.color(hex).rgb();
  const toward = (channel) => Math.round(channel + (255 - channel) * t);
  return `rgb(${toward(c.r)},${toward(c.g)},${toward(c.b)})`;
};

class SpendingTelescope extends HTMLElement {
  #payload;
  #path;
  #breadcrumb;
  #figure;
  #note;
  #live;
  #announced = false;

  connectedCallback() {
    const source = document.getElementById(this.source);
    if (!source) return;
    this.#payload = JSON.parse(source.textContent);
    this.#path = [this.#payload.tree];

    this.#breadcrumb = document.createElement("nav");
    this.#breadcrumb.className = "telescope-path";
    this.#figure = document.createElement("div");
    this.#figure.className = "telescope-figure";
    this.#note = document.createElement("p");
    this.#note.className = "quiet";
    // Where the telescope says what just changed: a polite live region, so a
    // drill-down is announced instead of silently redrawn under the reader.
    this.#live = document.createElement("div");
    this.#live.className = "visually-hidden";
    this.#live.setAttribute("aria-live", "polite");
    this.append(this.#breadcrumb, this.#figure, this.#note, this.#live);

    this.#render();

    // The bars are drawn at the width the cells have, so a new width is a new draw.
    let width = Math.round(this.clientWidth);
    let pending;
    new ResizeObserver(() => {
      const now = Math.round(this.clientWidth);
      if (now === width) return;
      width = now;
      clearTimeout(pending);
      pending = setTimeout(() => this.#render(), 120);
    }).observe(this);
  }

  get source() {
    return this.getAttribute("source") ?? "";
  }

  // Where the reader is, as labels: what `swap.js` carries across a swap of the page
  // to the telescope the new page builds. A label the new tree no longer has stops the
  // walk at the last one it does.
  get state() {
    return named(this.#path);
  }

  set state(labels) {
    if (!this.#payload) return;
    this.#path = walk(this.#payload.tree, labels);
    this.#render();
  }

  #render() {
    const here = this.#path.at(-1);
    let rows = here.children;
    this.#note.textContent = "";

    if (!rows.length) {
      this.#figure.replaceChildren(document.createTextNode("sin movimientos"));
      return;
    }

    const isLeaf = !rows[0].children.length;
    if (isLeaf && rows.length > LEAF_ROWS) {
      this.#note.textContent = `y ${new Intl.NumberFormat("es-AR").format(rows.length - LEAF_ROWS)} más`;
      rows = rows.slice(0, LEAF_ROWS);
    }

    this.#breadcrumb.replaceChildren();
    this.#path.forEach((node, index) => {
      if (index) {
        const step = document.createElement("span");
        step.textContent = "›";
        step.setAttribute("aria-hidden", "true");
        this.#breadcrumb.append(step);
      }
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = node.label;
      // Where the reader is now: the last crumb, filled. The others go back.
      if (index === this.#path.length - 1) button.setAttribute("aria-current", "location");
      button.addEventListener("click", () => {
        this.#path = this.#path.slice(0, index + 1);
        this.#render();
      });
      this.#breadcrumb.append(button);
    });

    // The label column is the shared one (`core/scale.js`), not this level's longest
    // label: the telescope's bars have to start on the same x as every other
    // chart's, or the eye re-zeros at each figure.
    const wanted = LABEL();
    // The figure steps that whole column to the left, so the bars land on the
    // text's edge and the labels read in the margin - where the page has the room
    // for it. Same step as `charts/mount.js`, read by the stylesheet as `--chart-outdent`.
    this.style.setProperty("--chart-label", `${wanted}px`);
    this.style.setProperty("--chart-outdent", wanted <= textMargin() ? `${wanted}px` : "0px");
    const span = rows.length - 1;
    const fill = (d, i) => lighten(color(d.bucket), span > 0 ? (i / span) * 0.5 : 0);

    // Three columns when the tree carries the months, one when it does not. Every
    // level gets them, the movement level included: there the month columns say
    // which of a payee's transfers are last month's and which are this one's.
    const columns = this.#payload.year !== undefined
      ? [
          { label: String(this.#payload.year), value: (d) => d.total },
          { label: this.#payload.previous_month, value: (d) => d.previous_month },
          { label: this.#payload.last_month, value: (d) => d.last_month },
        ]
      : [{ label: "", value: (d) => d.total }];

    // The three bar areas are the same width, and the row labels get their margin
    // on top of the first one: `[labels][bars][bars][bars]`. Equal columns would
    // leave the movement level - whose descriptions run to forty characters - with
    // a margin wider than the cell it sits in.
    const box = document.createElement("div");
    box.className = "telescope-columns";
    this.#figure.replaceChildren(box);

    const cells = columns.map(() => {
      const cell = document.createElement("div");
      cell.className = "telescope-column";
      box.append(cell);
      return cell;
    });

    // The columns go in first and empty, so the plot can be drawn at the width the
    // cell actually gets: a plot unit is then a CSS pixel, which is what lets the
    // title's indent land exactly where the bars start and keeps the type its
    // intended size. The width comes back from the browser on the read below.
    const row = Math.max(320, box.clientWidth);
    const labelRoom = Math.min(wanted, row * 0.45);
    const barRoom = Math.max(70, (row - labelRoom) / 3);
    cells.forEach((cell, index) => {
      cell.style.flexBasis = "0";
      cell.style.flexGrow = String(index === 0 ? labelRoom + barRoom : barRoom);
    });

    columns.forEach((column, index) => {
      const cell = cells[index];
      const width = Math.max(160, cell.clientWidth);
      const marginRight = Math.min(60, Math.max(16, Math.round(width * 0.3)));
      const marginLeft = index === 0 ? Math.max(60, Math.min(wanted, width - marginRight - 60)) : 8;

      if (column.label) {
        const label = document.createElement("div");
        label.className = "telescope-column-title";
        label.textContent = column.label;
        // The title sits over the bars, not the column's bounding box: indent it
        // by the same margin the plot reserves for the row labels.
        label.style.paddingLeft = `${marginLeft}px`;
        cell.append(label);
      }

      // A label longer than its margin would run off the left of the plot
      // instead of being cut, so it is cut with the charts' own scissors
      // (`charts/base.js`), estimated in the same chart ems.
      const fit = fitLabels(marginLeft);
      const max = Math.max(...rows.map(column.value));
      const y = { label: null, domain: rows.map((d) => d.label), ticks: index === 0 ? undefined : 0 };
      const svg = Plot.plot({
          width,
          style: { fontSize: BASE_FONT },
          height: Math.max(120, rows.length * ROW()),
          marginLeft,
          marginRight,
          marginTop: 6,
          marginBottom: 6,
          x: { label: null, grid: true, domain: [0, max * 1.35] },
          y: index === 0 ? { ...y, tickFormat: fit } : y,
          marks: [
            Plot.barX(rows, {
              x: column.value,
              y: "label",
              fill,
              ariaLabel: (d) => d.label,
            }),
            Plot.text(rows, {
              x: column.value,
              y: "label",
              text: (d) => money(column.value(d)),
              textAnchor: "start",
              dx: 6,
              fill: css("--ink-quiet"),
            }),
          ],
      });
      unlabel(svg);
      spines(svg, { left: marginLeft, right: marginRight, top: 6, bottom: 6 });
      cell.append(svg);
    });
    // A bar that opens a level is a button: keyboard-drillable and named, the
    // same way the breadcrumb's way back is a real button. A leaf bar is a
    // fact, not a door - no cursor, no tab stop.
    const drill = (labelled) => {
      const row = rows.find((d) => d.label === labelled.getAttribute("aria-label"));
      if (row?.children.length) {
        this.#path.push(row);
        this.#render();
      }
    };
    for (const g of box.querySelectorAll("rect[aria-label]")) {
      const row = rows.find((d) => d.label === g.getAttribute("aria-label"));
      if (!row?.children.length) continue;
      g.style.cursor = "pointer";
      g.setAttribute("role", "button");
      g.setAttribute("tabindex", "0");
    }
    box.addEventListener("click", (event) => {
      const labelled = event.target.closest("[aria-label]");
      if (labelled) drill(labelled);
    });
    box.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const labelled = event.target.closest("[aria-label]");
      if (!labelled) return;
      event.preventDefault(); // Space would scroll the page
      drill(labelled);
    });
    // Say where the reader landed, once it is a place they navigated to - the
    // first paint is the page's own heading's job.
    if (this.#announced && this.#live.textContent !== here.label) this.#live.textContent = here.label;
    this.#announced = true;
  }
}

customElements.define("spending-telescope", SpendingTelescope);
