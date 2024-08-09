from model_bakery.recipe import Recipe
from users.models import Profile

profile_recipe: Recipe = Recipe(Profile)  # type: ignore
