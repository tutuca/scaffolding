"""A login. A superuser is staff and sees everything."""

from scaffolding.data.models import BaseUser


def make_user(email: str = "user@example.com", password: str | None = None, *, superuser: bool = False) -> BaseUser:
    if superuser:
        return BaseUser.objects.create_superuser(email, password)
    return BaseUser.objects.create_user(email, password)
