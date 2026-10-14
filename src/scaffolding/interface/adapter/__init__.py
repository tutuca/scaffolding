"""Everything external. One subpackage per outside system.

`AdapterError` is the shared failure vocabulary: every adapter raises it or a
subclass, so a caller catches one type per outside system rather than one per
transport.
"""

from .exceptions import AdapterError

__all__ = ["AdapterError"]
