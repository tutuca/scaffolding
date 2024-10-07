
# from dj_rest_auth.registration.views import RegisterView
# from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path, include

# from . import views

urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls'))
]
