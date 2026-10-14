"""What the pager component is given: where the reader is, and where each way leads.

The links are the page's to write - which parameters a page keeps (the search, the order) is
its own business - so the component takes them made: an empty one is no way that way.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pager:
    page: int
    pages: int
    previous: str = ""
    next: str = ""
