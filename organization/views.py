from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from organization.models import Organization
from organization.serializers import OrganizationSerializer


class IsOrganizationAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.admins.filter(user=request.user).exists()


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizationAdminOrReadOnly)
