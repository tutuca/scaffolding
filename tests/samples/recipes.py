from model_bakery.recipe import Recipe
from samples.models import Sample

sample_recipe = Recipe(Sample)  # type: ignore
