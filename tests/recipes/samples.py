import pytest

from model_bakery.recipe import Recipe
from samples.models import Sample

sample_recipe = Recipe(Sample)


@pytest.fixture
def make_sample():
    def factory(**kwargs):

        return sample_recipe.make(**kwargs)
    return factory
