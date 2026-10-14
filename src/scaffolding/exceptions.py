"""Vocabulary shared by every layer. Imports nothing from the project."""

from collections.abc import Callable


class DomainRefusal(ValueError):
    """The caller asked for something the domain forbids.

    Not a server fault: a period that ends before it starts, authorizing an
    invoice that is not a draft, a portal CAE dated differently from the draft
    it belongs to. `ScaffoldingModelViewSet` answers these with 400.

    Raised by model mutators and by service functions. Distinct from Django's
    `ValidationError`, which the mutators raise for a value that is wrong on its
    own terms - an invoice with no exchange rate, a rate in the wrong currency -
    and which renders as a form error in the admin.

    Subclasses ValueError so the models stay usable outside HTTP: a script or a
    shell session sees an ordinary ValueError.
    """


def unless_refused[T](read: Callable[[], T]) -> T | None:
    """A read a page can do without: its value, or None when the domain refuses.

    For the figure that is one block of a page, where a refusal means "this block
    has nothing to say yet" and the rest of the page still stands.
    """
    try:
        return read()
    except DomainRefusal:
        return None


def refusal[T](read: Callable[[], T]) -> tuple[T | None, str]:
    """A read and the domain's own words when it refuses, for a block that says
    why it is empty. The same swallow as `unless_refused`, keeping the reason."""
    try:
        return read(), ""
    except DomainRefusal as error:
        return None, str(error)
