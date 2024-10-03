from django.contrib.auth.models import AbstractUser

from common.models import serializers

class User(AbstractUser):
    pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email"
        ]
