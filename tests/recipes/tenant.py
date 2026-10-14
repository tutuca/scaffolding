"""A tenant, by name. The slug derives from the name."""

from scaffolding.data.models import Tenant


def make_tenant(name: str = "Acme") -> Tenant:
    return Tenant.objects.register(name=name)
