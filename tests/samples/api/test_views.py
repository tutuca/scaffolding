import pytest
from samples.api import views

from django.urls import reverse


class TestBookingViewSet:
    viewset = views.SampleViewSet

    @pytest.mark.django_db
    def test_sample_api_list(self, rf):
        url = reverse("samples-list")
        request = rf.get(url)

        view = self.viewset.as_view({"get": "list"})

        response = view(request).render()
        assert response.status_code == 200
        assert response
