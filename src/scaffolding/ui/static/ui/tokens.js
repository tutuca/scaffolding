// The one reader for tokens.css: JS cannot see `var()` where Plot writes an
// SVG attribute, so a chart reads the computed value out of the document root
// and hands the library a real color. Kept apart from the widget so any other
// client-side drawing on the page reaches the tokens through the same door.
import { colorToken } from "./core/palette.js";

export const css = (name) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

// A color name -> a real color. The name -> token/literal mapping is `core/palette.js`'s
// pure `colorToken`; a `--var` resolves through the document, a literal passes
// through untouched.
export const color = (name) => {
  const token = colorToken(name);
  return token.startsWith("--") ? css(token) : token;
};

// The plot area keeps its left and bottom edge; the top and right are noise. Plot's `frame` mark draws all four - a rect cannot
// show two - and its axis marks draw nothing with the ticks off, so the edges are
// drawn here from the same margins the plot was given.
// How much margin the page leaves to the left of the text - its own indent, read
// off `main` rather than assumed from a breakpoint, so widening `--origin` widens
// the answer. The figures step their label column into it; a page that has not
// got the room answers zero and they keep their labels inside.
export function textMargin() {
  const main = document.querySelector("main");
  return main ? parseFloat(getComputedStyle(main).paddingInlineStart) || 0 : 0;
}

export function spines(svg, { left, right, top, bottom }) {
  const [width, height] = (svg.getAttribute("viewBox") || "0 0 0 0").split(" ").slice(2).map(Number);
  const line = (x1, y1, x2, y2) => {
    const el = document.createElementNS("http://www.w3.org/2000/svg", "line");
    el.setAttribute("x1", x1);
    el.setAttribute("y1", y1);
    el.setAttribute("x2", x2);
    el.setAttribute("y2", y2);
    el.setAttribute("stroke", css("--ink-quiet"));
    el.setAttribute("stroke-width", 1);
    svg.append(el);
  };
  line(left, top, left, height - bottom);
  line(left, height - bottom, width - right, height - bottom);
}

const pesos = new Intl.NumberFormat("es-AR");
export const money = (value) => pesos.format(Math.round(value));
