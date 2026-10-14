"""The app that holds what the tool looks like.

Templates and static files, and no views: every shell renders these, and
`ui/templates/admin/` and `ui/templates/allauth/` override templates that belong
to neither this project nor one shell of it. Putting them under the shell that
happens to hold `HomeView` would have meant reordering that shell in
`INSTALLED_APPS` for a reason that has nothing to do with its views.

At the project root rather than under `interface/`, because the layers table
defines `interface/` as what takes input from outside - HTTP, argv, an adapter -
and this takes none.

Its Python files are data and tools about the look, none of them a view: `contract.py` and `schema.py`
(what a model says to a page, read from `_meta` and from the API's schema), `forms.py` (the base every form of ours extends and the
renderer that gives it known markup), `pager.py` (what the pager component is given) and
`templatetags/grid.py` (a table column's head and cell). None imports a model of ours:
a model is passed in.
"""

from django.apps import AppConfig


class UiConfig(AppConfig):
    name = "scaffolding.ui"
    label = "ui"
