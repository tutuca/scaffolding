from django.db import models


class Role(models.TextChoices):
    """What a profile may do on one tenant.

    OWNER administers the tenant and its memberships; EDITOR works on its rows;
    VIEWER reads. The line between OWNER and EDITOR is managing access versus
    using it.
    """

    OWNER = "OWNER", "Owner"
    EDITOR = "EDITOR", "Editor"
    VIEWER = "VIEWER", "Viewer"
