import pytest

from model_bakery.recipe import Recipe
from users.models import User, Profile

user_recipe = Recipe(User)
profile_recipe = Recipe(Profile)


@pytest.fixture
def make_user():
    def factory(**kwargs):
        return user_recipe.make(**kwargs)

    return factory


@pytest.fixture
def make_profile(make_user):
    def factory(user=None, **kwargs):
        if user is None:
            user = make_user()
        return profile_recipe.make(user=user, **kwargs)

    return factory
