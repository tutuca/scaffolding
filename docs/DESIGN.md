# DESIGN — the one language

The look is one language: server-rendered Django templates plus a small set of
vanilla-JS modules and components. No build, no framework.

## Tokens

`src/scaffolding/ui/static/ui/tokens.css` and `tokens.js` are the single source of
truth for the palette and spacing. A color or spacing change is one edit in one
place.

## Components

Each component is a folder under `ui/static/ui/components/<name>/` with its
template (`ui/templates/ui/components/<name>/`) and, when it is interactive, a JS
module:

- `form/` — the base renderer (`ui/forms.py`) gives every form the same markup.
- `icon/`, `action/`, `dialog/`, `pager/`, `search/` — the small building blocks.
- `grid/`, `table/` — data display, driven by the `data-grid`/`data-table`
  custom elements in `main.js`.

## Rules

- A page template extends `ui/base.html` and fills `{% block main %}`.
- A form is a plain `forms.Form`; a model's fields are assigned by its mutators,
  never by a `ModelForm`.
- After changing what a page looks like, run `uv run python bin/ui_shot.py` against
  a running server and check `var/shots/` before claiming done. The checkable
  rules live in `tests/scaffolding/ui/`.
