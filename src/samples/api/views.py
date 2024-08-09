from rest_framework import permissions, throttling, viewsets

from .. import models


class SampleViewSet(viewsets.ModelViewSet):
    serializer_class = models.SampleSerializer
    queryset = models.Sample.objects.all()
    throttle_classes = [throttling.AnonRateThrottle]
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
