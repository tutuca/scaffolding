// Commands without a refresh: a form or link marked `data-swap` is sent with
// `fetch`, and the page that comes back replaces `<main>`.
//
// The server has one way to answer - a whole page, after a redirect or with a 422
// and the form's errors - so this script knows nothing about goals or fields.
// `fetch` follows the redirect itself. What every request needs around it is a
// decorator (`core/pipeline.js`): one at a time, the newest read wins, the
// browser's own submission when no answer came, and `aria-busy` while it is out.
// CSRF rides along: `FormData` carries the form's `csrfmiddlewaretoken`.
import { Unreached, compose, fallback, latest, once } from "./core/pipeline.js";

/** `<main>` says it is busy while any request is out; the stylesheet shows it. */
const busy = (next) => {
  let out = 0;
  return async (request, native) => {
    out += 1;
    document.querySelector("main").setAttribute("aria-busy", "true");
    try {
      return await next(request, native);
    } finally {
      out -= 1;
      if (!out) document.querySelector("main")?.removeAttribute("aria-busy");
    }
  };
};

/** Ask, and put the answer on the page. A page with no `<main>` is not ours (a proxy's
 * error, say): it is shown as it came, never asked for again. */
async function page(request) {
  let response;
  try {
    response = await fetch(request);
  } catch (error) {
    throw new Unreached(error.message);
  }
  const answer = new DOMParser().parseFromString(await response.text(), "text/html");
  const next = answer.querySelector("main");
  if (!next) {
    document.documentElement.replaceWith(answer.documentElement);
    return;
  }
  // What the reader has opened in a widget that keeps its own view state is carried
  // over to the same widget (by id) in the new page.
  const kept = new Map([...document.querySelectorAll("[data-keep]")].map((element) => [element.id, element.state]));
  // A widget the first page had no use for is loaded when the answer brings one.
  if (next.querySelector("data-table")) await import("./table/table.js");
  if (next.querySelector("data-grid")) await import("./grid/grid.js");
  document.querySelector("main").replaceWith(next);
  for (const element of next.querySelectorAll("[data-keep]")) {
    if (kept.get(element.id)) element.state = kept.get(element.id);
  }
  document.title = answer.title;
  if (response.ok) history.replaceState(null, "", response.url);
  // The figures are drawn by the vendored Plot, which `main.js` loads only on a
  // page that has some; a page that had none has nothing to redraw here either.
  // A dialog the server sends open is a form that was refused: it was shown inline
  // for the browser without this script, and here it is the modal it should be.
  for (const dialog of next.querySelectorAll("dialog[open]")) {
    dialog.close();
    dialog.showModal();
  }
  // Where the link pointed, or the first field that erred.
  const anchor = document.getElementById(new URL(request.url).hash.slice(1));
  (next.querySelector("[aria-invalid]") ?? anchor)?.scrollIntoView();
  // A swap replaces the page the reader's focus lived on, so focus dies with
  // it: put it on the field that erred (a refused form), or leave it on the
  // dialog the refusal opened, else put it back on `<main>` itself, which
  // carries `tabindex="-1"` for exactly this.
  (next.querySelector("[aria-invalid]") ?? next.querySelector("dialog[open]") ?? next).focus();
}

const send = compose(fallback, once, latest, busy)(page);

/** A form as a request: a GET carries its fields in the address, as the browser would. */
function requestOf(form, submitter) {
  const data = new FormData(form, submitter);
  if (form.method.toLowerCase() !== "get") return new Request(form.action, { method: form.method, body: data });
  const url = new URL(form.action);
  for (const name of new Set(data.keys())) url.searchParams.set(name, data.get(name));
  return new Request(url);
}

document.addEventListener("submit", (event) => {
  const form = event.target.closest("form[data-swap]");
  if (!form || event.defaultPrevented) return;
  event.preventDefault();
  send(requestOf(form, event.submitter), () => form.submit());
});

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-swap]");
  if (!link || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.button) return;
  event.preventDefault();
  send(new Request(link.href), () => location.assign(link.href));
});
