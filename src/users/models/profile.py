
from common.models import models, serializers
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField()
    date_modified = models.DateField()

    def __str__(self):
        return self.user.username


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ["user", "date_created", "date_modified"]
