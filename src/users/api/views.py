
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
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



class AuthToken(ObtainAuthToken):
    throttle_classes = [throttling.AnonRateThrottle]
 
    class Meta:
        fields = ['token', 'user']
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': user,
        })