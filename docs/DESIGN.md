# DESIGN — the one language

2026-09-19. Decision-first: each rule is ours, with the source that argued it
and the check that enforces it — or the honest "judgment; review question".
Spec and survey evidence: the 2026-09-19 one-language spec, in git history.

## The document tells a story

A page is prose with structure, not divs with paint. Landmarks (`header`,
`nav`, `main`, `footer`), one `h1`, headings that never skip a level, labels
on every input, names on every `img` and frame. It must read with CSS off.
(Semantic HTML: css-tricks; progressive enhancement.)
Check: `tests/scaffolding/ui/test_story.py`, `tests/scaffolding/interface/web/test_chrome.py`.

## Typography first

One measure (`--measure`), one scale (`--ratio`, three named steps), rhythm in
`--gap` multiples. Line length before font choice; the fonts are the system's,
and all sans — decided 2026-09-19 against serif headings: this is an
instrument, not a publication, and the identity lives in the chart blue.
(webtypography.net.) Check: sizes come from the scale — a literal size in a
stylesheet is a review flag.

## CRAP

Contrast is hierarchy, not decoration — if two things differ, make them
plainly different; token pairs used together clear WCAG AA 4.5:1. Repetition
is the tokens: one place declares a value. Alignment is the one column.
Proximity is spacing in `--gap` stops — related things share a stop, unrelated
things get a bigger one. (Williams.) Check: `test_contrast.py` for contrast;
the rest is judgment at the shots.

## Less design

Content-out sizing, flex and grid over positioning, no framework, no reset
beyond box-sizing plus four rules from Comeau's public-domain reset. A rule
earns its place by displacing a future ad-hoc rule. Composition is four
primitives written fresh (Every Layout): the stack (`main > * + *`), the
cluster (the nav row), the center (the measure column) and the breakout
(`.chart`, a figure that spans the page). Order of resort
(CUBE): cascade first, composition second, exceptions rare and named.
Nesting groups a component's rules under its root selector (native CSS nesting
- the browser's module system, no build), and a spacing value is a `--gap` stop
(`calc(var(--gap) * n)`) or a named token, never a bare rem. The support floor
is declared, not polyfilled: the latest Firefox and Chrome and nothing else (Safari is out
of scope, 2026-10-08), since we already lean on
`color-mix`, `svh` and nesting.
(A List Apart, "Designing for the Unexpected"; every-layout.dev; cube.fyi.)
Check: judgment; the surveys' numbers live in the spec.

## Color

Ten literal free choices in `tokens.css` — two poles, two hues, gap, radius,
ratio, measure, two font stacks — and every other value an expression of them
(`color-mix`, `calc`). Nothing outside `tokens.css` names a color; charts are
the one exemption. (RefactoringUI, taken for
"declare shades deliberately", declined for "declare them all up front".)
Check: `test_tokens.py` (no color literal outside `tokens.css`),
`test_contrast.py`.

## The user first

Accessibility is quality, not garnish: focus visible, errors beside what
erred, `prefers-reduced-motion` honored the day motion arrives, nothing
offered that will refuse you. NN/g's ten heuristics are the review questions.
Check: the mechanical part in `test_story.py`; the rest is the review.

## UI as a program

A page is a pure function of the read model its view passes; no state hides
in markup; no class ships without a consumer; one owner per value. (acko.net,
cut to what server-rendered HTML can honor.) The one interactive widget holds
the same rule on the client: a custom element (`<spending-telescope>`) whose
read model is the JSON the view embeds, whose state is its own path, and whose
markup stays in the light DOM so `page.css` keeps dressing it. (Vanilla custom
elements + ES modules, no build.) Classes by review.

## Frontend units

A page is assembled from units, and a unit is one name shared by three assets:
the template partial that mounts it, the JavaScript that renders it, and the
CSS that dresses it. `telescope` is `telescope.js` + `telescope.css` + the
`<spending-telescope>` element; `charts` is `charts/` + `charts/charts.css` +
the `data-chart` mounts. One `main.js`, loaded once in the base, is the
entrypoint: it lazy-loads the vendored Plot/d3 and the unit a page actually
mounts, so a page with no figures downloads none of it. The class names a
module writes into the light DOM are
the same class names its CSS file dresses, and the two sit side by side, so
reading the JS shows you where its CSS is. `core/` and `tokens.js` are the pure
half (browser-free, `node --test`) and own no CSS.

The state contract above, made mechanical: a widget is a custom element whose
state is private fields, whose markup is derived by one `render` from that
state, and whose events mutate the state and re-render - never edit the DOM
directly. The charts are the read-once case of the same shape:
`render(readModel) -> DOM`, mounted from the JSON the view embeds. No shadow
DOM, no build - light DOM so the token cascade keeps dressing everything.
Check: review - a class the JS writes keeps its rule beside it.

## Commands

2026-10-08. The one interactive widget holds view state; a *command* changes the
ledger, and the ledger is the one world. A command is a plain form `POST` to its
own resource (`/notebooks/planes/metas/`) that answers with the whole page: a
redirect when it took, the same page at 422 with the errors beside the fields when
it did not. Every figure is derived again from the one ledger, so nothing on the
page can disagree with what was just entered. `swap.js` is the enhancement, not the
mechanism: a form marked `data-swap` is sent with `fetch`, `<main>` is replaced by
the answer's, the figures are redrawn, and a request that got no answer falls back
to the browser's own submission. What every request needs around it is a decorator
(`core/pipeline.js`, after acko.net's "Climbing Mt. Effect": a send takes a request and
the native action, a decorator wraps a send, exit under entry): `once` (one command at
a time, so a double click is one goal), `latest` (a newer read aborts an older one,
a command is never aborted), `fallback` (only for a request nobody answered - a POST
the server did answer is never sent twice) and `busy` (`aria-busy` on `<main>`). CSRF is Django's token in the form; `FormData` carries it.
Considered and declined: fragment envelopes and a header to ask for them, per-region
hashes, a client-side store, and posting to the JSON API (a form cannot degrade to
JSON, and the client would need a second renderer). Cost accepted: each command
recomputes the page - measured 2026-10-08 on the real ledger through the dev server,
0.37 s for `/notebooks/planes` and 0.48 s for `/notebooks/movimientos`. A widget that keeps
its own view state declares `data-keep` and a `state` property, and `swap.js` carries
it by id into the new page: the telescope's zoom is a list of labels, walked again in
the new tree (`core/path.js`), so naming a movement does not send the reader back to
the root. A command is a `Command[Form]` view (`books.py`): which form it reads, what
to run, how to show the page again around a refused one. Goals, their order and the
naming of unnamed movements are the three so far. Check:
`tests/scaffolding/interface/web/test_plans.py`; the swap itself is looked at in the
browser.

## Controls

2026-10-08. Buttons, fields and forms are one stylesheet, the form component's
`components/form/form.css`, beside `form.js` and loaded with every page - an
expression of the tokens like everything else: the brand pole is the one action
colour, the line is every border, the danger hue is only ever an error. Two weights
of button, chosen by what the button does and not by a class: one that submits is the
action (filled), one that does not - open a dialog, cancel, hand the order back to the
plan - is the way around it (outlined). A form is Django's div layout (`{{ form }}`):
short fields pair two to a row while the
box holds two, long ones and everything that is not a field take the row. State comes
from attributes the platform already sets (`aria-invalid`, `:user-invalid`, `type`,
`::file-selector-button`, `accent-color`), so a new form arrives dressed with no markup
of ours. A form that interrupts the page is the `dialog` component: a native `<dialog>` opened by
`command="show-modal"`: no script to open or close it, and focus, Esc and the backdrop
are the browser's (`closedby="any"` makes a click outside cancel); the server sends a refused form's dialog `open`, which is an inline
box without a script and a modal once `swap.js` upgrades it. A number a person does
not want to type is a widget over the number (a row's drag handle, below): the form posts
the same integers with or without it, and a table opened and saved untouched writes
nothing. The one focus ring is `page.css`'s; `action.css` only recolors it.

A form's fields share rows: each field is a subgrid of three rows (label, hint, widget); the
messages hang under the widget without taking a row, so one appearing moves nothing. Paired fields line up whatever their hints say. Controls have one height and
a select draws its own arrow. What commits is green (`--ok`, derived from the income
colour); what only filters (a GET form) keeps the brand colour. In a dialog the submit
sits at the far edge from Cancelar.

Considered and declined: Pico, PlainCSS and the "modern CSS, no framework" write-ups
(2026-10-08). Pico and PlainCSS bring their own tokens and a class vocabulary, which is
the second source of truth this file exists to prevent, and what they do for forms is
a short list we already had or took: full-width fields, a muted hint, `aria-invalid`,
`accent-color`. Taken from them: `accent-color`, `:user-invalid`, button weights, the
hint under the label. Support floor for all of it: the latest Firefox and Chrome.

## The table and the grid

2026-10-08. Two components, the way `partner_next` (a React front end) has them:
a dumb `Table` that owns rendering and styling and is built to be extended, and the
`DataExplorer` that layers search, sort and paging around it. Here:

**The table** (`ui/table/`): every table on the page is a `.table-scroll` box holding a
`<table>`, and `table.css` is its whole look (ruled under the head and between rows, money
right-aligned in tabular numerals, scrolling in its own box so the page never does). It
works with no script at all. `<data-table>` (`table.js`) is the primitive with a model:
the server's markup left alone, the columns read from the headers (`data-key`, and
whatever a feature wants a header to say), the rows from the body (`data-key`), the
natural order, and a draw that runs the features' stages over it. It has no features of
its own; `static features` is the extension point, an ordered table of name -> loader,
and a feature is `(host) => { name, stage?, refresh?, state }` - `stage(rows)` returns the
rows as it would show them, `refresh()` runs after the draw, `state` is what a swap of
the page carries across (the element is `data-keep`; the state waits for the features to
load). A feature finds its own markup and does nothing when it is absent.

**The grid** (`ui/grid/`): `<data-grid>` is the table with every feature, a subclass that
lists them. Which a grid uses is written in its markup, as partner_next writes it in a
column's `isSortable`: a header with `data-sort="number|text"` sorts, an
`input[data-filter]` filters, a row with a `rank_<id>` input moves, and a column whose
header says `data-derived` is what only the server can recompute after a move. Each
feature has the version that works without the script - sort is the server's order,
filter and paging are a GET form and links, reorder is a number input and a form - and
the pure parts are tested apart from the DOM (`core/rows.js`, `core/sort.js`).

- `sort`: a header becomes a button cycling ascending, descending, natural (`aria-sort`
  says which); a cell sorts by its `data-value` when the server wrote one (money shows
  "3.0 M" and sorts as 3000000), empty cells go last either way.
  On a grid that is one page of many the client cannot sort what it does not have, so
  there the header is a link and the server orders (`?s=importe&d=ascending`, over every
  match, `aria-sort` set by the server): the raw movements, whose default is the biggest
  first. The order travels with the search and the page, in the pager's links and in the
  naming form's hidden fields.
- `filter`: the search box inside the grid narrows the rows on the page as the reader
  types - a cell that holds a control is left out of what a row says, since a dropdown's
  options are the whole vocabulary - and hides them. It is the near half of a search whose
  far half is a GET form: Enter searches every unnamed movement the server has
  (`expenses.unnamed_page(search, page)`), and the pager is links that carry `?q=&p=`.
  `swap.js` sends a GET form as a GET and replaces the address, so a result is a URL; the
  naming form carries the same `q` and `p`, so naming from page 3 comes back to page 3.
- **The model** (2026-10-09). The state of an order is not in the DOM: `core/ordering.js`
  owns it - the order now, whose it is (the person's or the plan's), whether it differs
  from what is saved, which order the derived figures are for - and every change to it is
  named for what happened (`moved`, `leftToPlan`, `discarded`, `shownFor`); what to write
  (`ranks`), what is out of date (`stale`) and what to ask the server (`asking`) are derived
  from those four facts. It is browser-free and tested at 100% with `node --test`;
  `reorder.js` is the shell around it - the sensors tell the model what the person did and
  one `render` draws the rows, the numbers, the table actions and the stale mark from it.
  Built bottom-up from what `reorder.js` was already holding, not from a general idea of a
  model. Two things the iteration moved into place: the markup is read *once*, into records
  (`{ key, title, rank }`), and from then on the model and the rows meet by key; and the
  grid is *told where its model answers* - `data-preview-url` is a URL with `{keys}` where the
  order goes, written by the server partial - so `preview.js` knows no page's address.
  What else a grid's model should own (creating rows) waits for the next thing that needs
  it to say.
- **The table's actions** are one section above the table (`.table-actions`, a toolbar):
  *Agregar meta* at the left, and at the right what can be done to an order that is not
  saved - the note, Guardar orden, Descartar, Que el plan decida - which appear when the
  model says there is something to save. Without a script the section is the form of
  numbers and its one button.
- `reorder`: the server draws a handle beside each rank number, hidden; the feature
  shows it. The moving itself is `grid/sortable.js`, after Shopify's Draggable
  (shopify.github.io/draggable): sensors turn what the reader does into one vocabulary -
  pick up, sort, drop, cancel - and the rest only listens. The pointer sensor (mouse, touch
  and pen are one thing to pointer events; a drag starts only on the handle, so a finger
  still scrolls the page) shows a *mirror*, a copy of the row that follows the pointer,
  while the row itself stays in the list, quiet, as the place it will land, and the list is
  reordered as the pointer crosses a neighbour's middle. The keyboard sensor is the WAI-ARIA
  pattern (Draggable leaves it to a plugin): Space or Enter picks the row up
  (`aria-pressed`), the arrows move it, Space or Enter drops it, Escape puts it back, and
  arrows on a row that is not held do nothing; every step is announced in a live region.
  While a row is moving nothing is written and nothing is asked. On a *drop* the numbers are
  written into the inputs and the grid asks the page what it would say with that order
  (`?orden=3,1&vista=metas`: the same `readiness` that draws the saved page, without the rest
  of the page - 180 ms against 400 on the real ledger - and the grid and the sentence come
  from the same partials as the page, so the two cannot drift), after a 300 ms wait, once per
  drop, abortable, and never for an order that is already the one on screen. It takes from
  the answer only what the order changes: the elements marked `data-preview` (the sentence
  and the figure) and the cells of the columns marked `data-derived`, row by row
  (`preview.js`). From the drop until the answer is merged those cells are dimmed as stale. An
  order dragged back to where it began is not saved, asks nothing, and puts the saved
  numbers back; Descartar does the same and asks for the saved page once if a what-if had
  replaced it. "Que el plan decida" - which a list of keys cannot ask - stays stale until
  saved. A bar says which (Guardar, Descartar, Que el plan decida). A refused order keeps
  the plain inputs so the wrong numbers can be seen, and while the grid is sorted by a column
  the handles are off. Replaced the same day: an order dialog with a `<sortable-list>` of its
  own - the table is the list, and the number is the same - and a version that moved the row
  itself under the pointer and asked the server on every move (the jitter and the dozens of
  requests this one removes).

**Naming many at once.** 1065 unnamed movements are not 1065 decisions: a row whose payee
(`payee_of`, who the line paid) appears among the other unnamed ones has a toggle beside
its dropdown - a small box in a column every row reserves, so the dropdowns line up whatever the
words are - whose label ("y los N de «payee»") floats over the row only while the box is pointed
at or has the cursor, and is always its accessible name; ticking it spreads that categoría to
all of them
(`expenses.name_with_payees`, one pass over the ledger; a categoría given to a row on its
own wins over the one spread to it). The count is over every unnamed movement, not the
page or the search, so searching one word never hides that the payee is elsewhere. This
names the movements that exist; a rule for the ones that will arrive is the ledger's
`categorias.tsv`, not this page.

**Closing a goal** has two exits and a way back: *cumplida* (it happened) and *quitar* (it
no longer matters) both leave the plan and stay on the books, and a list under the table,
"Cumplidas y descartadas", gives each a button to return it to the plan - pending and with
no place in the order, since the place it had is not a place among the goals ranked since.

**On a phone.** The pointer sensor is touch-ready (checked 2026-10-09 by emulated touch over the
DevTools protocol: the mirror follows the finger, the page does not scroll under it, a drop
writes the numbers and asks once) but only if the handle is on screen, and in a table wider than
the screen the last column is off to the right. So the actions column is `position: sticky` at
the scroll box's right edge (`grid.css`): the verbs and the handle are always within reach and
the other columns scroll under. The order's bar says `Sin guardar` (plus `fechas por recalcular`
while the what-if is out) so that it fits the row it appears in at 1280 and the table does not
move under the reader's hand.

**Actions** are the other half of partner_next's design (`actionsColumn`: a column
declared by its actions, each a label, a variant and a callback). The page's version is
`ui/action.html`, one partial for both levels: a row's actions are icon buttons in the
last column (`acciones`: move, edit, quitar), and the table's own action - add - is the
same button with its word beside the icon. Each opens a native dialog by
`command="show-modal"`; the one that discards (`data-danger`) asks first, and quitar
does not delete: a goal is set to dropped and stays on the books. Icons are one sprite,
`icons.svg`, drawn in `currentColor` with no library; an icon-only button is named for
the screen reader and the tooltip by its markup.

Two grids so far: the goals on the plans page (sort, reorder, actions) and the raw detail
on movimientos (sort, filter, a page of 25 beside the dropdown that names each) - the
second took no change to the element, only markup, which is what the seam was for.

Not taken from `partner_next`: columns derived from a schema (a Python `Column`
declaration that renders the markup is the later equivalent, once a third grid needs the
types) and loading/empty states (the server renders those).

## Components

2026-10-09. A component is a name that up to three files share, and nothing else -
`templates/ui/components/<name>/<name>.html` (the markup a page includes),
`static/ui/components/<name>/<name>.js` and `.css` (what dresses and enhances it) - any of
them, never none, always named for the directory (`<name>_<part>` for a second template, the
form's `form_field.html`). The markup is the component; the script and the stylesheet are
sprinkled on it, so a page works with neither, and no script builds markup that the server
could have drawn (the browser's message for a field has a slot in the form's own template,
which `form.js` fills). `tests/scaffolding/ui/test_components.py` enforces the names.

So far: `icon`, `action` (a button that opens a dialog; the icon alone, or with its word),
`dialog` (a question, with a form or without; the server sends it `open` when it is a refused
form again), `pager`, `search` (a Django form sent by GET), and `form` (no markup of its own to
include: Django's renderer templates are the markup, `form.js` fills their slots, and
`form.css` dresses every control). A page asks
for one with `{% include "ui/components/<name>/<name>.html" with ... %}`; an include sees the
caller's whole context, so a component is told what it must *not* show as explicitly as what
it must (a dialog that only asks is given `form=None`, because the page's loop had a `form`).
Assets are listed in `base.html`; gathering them from the components a page used is tabled.

**The contract.** What a model says to the UI is read, not written: `ui/contract.py` lists
an instance's fields from `_meta` (`Contract.of(model, fields=..., exclude=...)`, the way a
`ModelForm`'s `fields` names them), and builds the default form from them - Django's own
`Field.formfield()` per field, with `FORMFIELD_OVERRIDES` (the admin's `formfield_overrides`
shape; replace entries by passing others) for what the browser should be given. A plain
`forms.Form`, not a `ModelForm`: model fields are assigned by the model's mutators and by
nothing else. An explicit `<Model>Form` in the module the caller names wins by convention;
without one the form is generated (`goal_form` is `form_for(Goal, fields=GOAL_FIELDS, ...)`
and there is no hand-written goal form). Labels and hints are the model's `verbose_name` and
`help_text`, in Spanish (i18n is deferred: Spanish for the user, English for the code).
`ui/schema.py` reads the same fields as the API describes them (`/api/schema/`: label, hint,
`type` and `format`, `maxLength`, `nullable`, `enum`, `readOnly`); `test_schema.py` keeps the
two readings in agreement, and where they differ on purpose (a field with a default is not
required of a request but is of a form) it says so. The grid reads the schema: `{% head schema
"amount" %}` writes a column's `<th>` - label, `data-key`, the kind it sorts by, whether it is
right-aligned - and `{% cell schema "amount" value %}...{% endcell %}` the `<td>` under it,
owning what the kind decides and leaving what is shown to the page. A read model has no schema;
the page declares what it shows.

**Validation, on both sides, one markup.** The browser validates from the attributes the widgets
emit (`required`, `maxlength`, `step`, `type=date`); `form.js` shows its message in the field's
own slot while the reader types (silent until the field has been left, current after) and for
every field at once on a send, with the cursor in the first. The server's errors - a field's, the
form's, and the domain's refusals - come through `{{ form }}`, Django's markup, and a form
whose fields sit in table cells draws one list, `{{ form.summary }}`. A rule the model can hold
(`amount > 0`) is a constraint, said in words first by the entry point that writes it
(`refuse_not_positive`); the client does not re-derive it.

**Method.** `bin/ui_shot.py --out var/shots-baseline` keeps a baseline (the eight surfaces at 360
and 1280, with and without scripting, and the states a surface does not show alone: dialogs
open, an order moved); `bin/ui_diff.py` compares a fresh set against it, per shot, in changed
pixels. A move of markup into a component is done when every shot is 0.00%.

## Ownership

Vanilla Django admin and vanilla Notebook are the base — both theme by
documented CSS variables (42 and 221; surveys in the spec, all packaged
themes declined 2026-09-19). Four admin templates are vendored and edited to
wear the chrome; `test_vendored.py` pins each to the sha256 of its upstream
origin, so an upgrade that moves one fails loudly and the re-diff is a named
task. The books are pages whose figures draw client-side with Observable Plot
(`charts/mount.js` reads the JSON read model `interface/web/charts.py` emits and
colors it through `tokens.css`).

## The method

A change under `src/scaffolding/ui/` or to any template is not done until
`bin/ui_shot.py` has rendered its shots and they have been looked at — claims
about a page cite the shot. Claude-in-Chrome is the interactive tool; the
shots are the record. The tests above carry the rules; this file carries the
why; changes to either land together.
