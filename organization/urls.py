from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from organization.views import OrganizationViewSet, GroupViewSet

router = routers.DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
