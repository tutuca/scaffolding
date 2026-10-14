"""Where a Google consent is written down.

allauth owns these tables, so they have no mutators to call - but the write
still belongs to the data layer, and the gateway and `scaffolding login` both end
here rather than each writing the row their own way.
"""

from allauth.socialaccount.models import SocialAccount, SocialToken

from scaffolding.data.models import BaseUser

PROVIDER = "google"


def record_google(user: BaseUser, *, access: str, refresh: str) -> SocialToken:
    """Store what Google returned, replacing any earlier consent.

    Replacing, not appending: two rows would leave whichever was found first in
    charge of the archive.
    """
    account, _ = SocialAccount.objects.get_or_create(user=user, provider=PROVIDER, defaults={"uid": user.email})
    token, _ = SocialToken.objects.update_or_create(
        account=account, defaults={"token": access, "token_secret": refresh}
    )
    return token


def google_token(user: BaseUser) -> SocialToken | None:
    return SocialToken.objects.filter(account__user=user, account__provider=PROVIDER).first()
