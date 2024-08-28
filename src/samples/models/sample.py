from common.models import models, serializers


class SampleTypeChoices(models.TextChoices):
    default = ("default", "Default")
    special = ("special", "Special")


class SampleType(models.Model):
    name = models.CharField(max_length=255, choices=SampleTypeChoices.choices, default=SampleTypeChoices.default)

    def __str__(self):
        return self.name


class Sample(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    sample_type = models.ForeignKey(SampleType, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class SampleSerializer(serializers.ModelSerializer):
    sample_type = serializers.StringRelatedField()

    class Meta:
        model = Sample
        fields = ["title", "description", "sample_type"]
