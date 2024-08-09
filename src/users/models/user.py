from common.models import serializers
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ...


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
