from rest_framework import routers
from samples.api.views import SampleViewSet
from users.api.views import UserViewSet


router = routers.DefaultRouter()

router.register("samples", SampleViewSet, basename="samples")
router.register("users", UserViewSet, basename="users")
