import pytest


@pytest.mark.django_db
def test_profile_create(make_profile):
    profile = make_profile()

    assert profile
    assert str(profile)


@pytest.mark.django_db
def test_user_create(make_user):
    user = make_user()

    assert user
    assert str(user)
