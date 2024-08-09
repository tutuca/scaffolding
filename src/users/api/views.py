from rest_framework import permissions, throttling, viewsets
from .. import models


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = models.UserSerializer
    queryset = models.User.objects.all()
    throttle_classes = [throttling.AnonRateThrottle]
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = models.ProfileSerializer
    queryset = models.Profile.objects.all()
    throttle_classes = [throttling.AnonRateThrottle]
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
