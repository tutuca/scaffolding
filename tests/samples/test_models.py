import pytest
from .recipes import sample_recipe


@pytest.mark.django_db
def test_sample_create():
    sample = sample_recipe.make()

    assert sample
    assert str(sample)
    assert str(sample.sample_type)
