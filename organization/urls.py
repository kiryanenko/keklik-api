from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from organization.views import OrganizationViewSet

router = routers.DefaultRouter()
router.register(r'organizations', OrganizationViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
