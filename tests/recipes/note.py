from model_bakery.recipe import Recipe

from scaffolding.data.models import Note

note = Recipe(Note, title="A note")
