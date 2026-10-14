"""The one door, and the guard on it.

allauth lets any Google account sign up, which is the wrong default for a
ledger. An empty allowlist here means *nobody* - the direction that fails safe,
and what made it safe to wire the gateway before the books had owners.
"""

from typing import cast

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.conf import settings
from django.forms import ModelForm
from django.http import HttpRequest

from scaffolding.data.models import BaseUser


class GatewayAdapter(DefaultSocialAccountAdapter):
    """Refuses unlisted addresses, and creates the one thing a user starts with."""

    def may_signup(self, email: str) -> bool:
        allowed = {address.strip().lower() for address in settings.SIGNUP_ALLOWED_EMAILS}
        return bool(email) and email.strip().lower() in allowed

    def is_open_for_signup(self, request: HttpRequest, sociallogin: SocialLogin) -> bool:
        return self.may_signup(sociallogin.user.email or "")

    def save_user(self, request: HttpRequest, sociallogin: SocialLogin, form: ModelForm | None = None) -> BaseUser:
        """The login, the name Google returned, and a way in.

        Not a `Taxpayer`: signing up does not make someone one, and an accountant
        never becomes one. Entering a CUIT creates books.

        It created a `Profile` here too until 2026-09-18, which made this the one
        place a person existed and every other path a bug waiting to be found.
        The person is a column on the login now, so there is nothing to forget.
        """
        user = cast(BaseUser, super().save_user(request, sociallogin, form))
        user.record_name(sociallogin.account.extra_data.get("name", ""))

        # The admin is this tool's UI, so logging in has to reach it. What is in
        # it is decided by OwnedAdmin and data/visibility.py, not by this flag.
        user.open_admin()

        return user
