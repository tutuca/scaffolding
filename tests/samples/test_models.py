import pytest


@pytest.mark.django_db
def test_sample_create(make_sample):
    sample = make_sample()

    assert sample
    assert str(sample)
    assert str(sample.sample_type)
