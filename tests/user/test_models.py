import pytest
from .recipes import profile_recipe


@pytest.mark.django_db
def test_profile_create():
    profile = profile_recipe.make()

    assert profile
    assert str(profile)
