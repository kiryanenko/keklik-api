from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from organization.views import OrganizationViewSet, GroupViewSet, GroupMemberViewSet

router = routers.DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'members', GroupMemberViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
