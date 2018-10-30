from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api.utils.views import status_text
from organization.models import Organization, Group
from organization.serializers import OrganizationSerializer, GroupSerializer, AdminSerializer, AddAdminSerializer, \
    DeleteAdminSerializer


class IsOrganizationAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        organization = obj if isinstance(obj, Organization) else obj.organization
        return organization.admins.filter(user=request.user).exists()


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizationAdminOrReadOnly)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: AdminSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Organization not found.'
        }
    )
    @action(detail=True)
    def admins(self, *args, **kwargs):
        """ Список админов организации. """
        organization = self.get_object()
        admins = organization.admins.all().order_by('id')
        return Response(AdminSerializer(admins, many=True).data)

    @swagger_auto_schema(
        request_body=AddAdminSerializer,
        responses={
            status.HTTP_201_CREATED: AdminSerializer,
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN),
            status.HTTP_404_NOT_FOUND: 'Organization not found.'
        }
    )
    @admins.mapping.post
    def add_admin(self, request, *args, **kwargs):
        """ Добавление админа к организации. """
        serializer = AddAdminSerializer(data=request.data, context={'organization': self.get_object()})
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        return Response(AdminSerializer(admin).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=DeleteAdminSerializer)
    @admins.mapping.delete
    def delete_admin(self, request, *args, **kwargs):
        """ Удаление админа из организации. """
        serializer = DeleteAdminSerializer(data=request.data, context={'organization': self.get_object()})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: GroupSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Organization not found.'
        }
    )
    @action(detail=True)
    def groups(self, *args, **kwargs):
        """ Список групп организации. """
        organization = self.get_object()
        groups = organization.groups.all().order_by('-id')
        return Response(GroupSerializer(groups, many=True).data)

    @swagger_auto_schema(
        request_body=GroupSerializer,
        responses={
            status.HTTP_201_CREATED: GroupSerializer,
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN),
            status.HTTP_404_NOT_FOUND: 'Organization not found.'
        }
    )
    @groups.mapping.post
    def create_group(self, request, *args, **kwargs):
        """ Добавление группы к организации. """
        serializer = GroupSerializer(data=request.data, context={'organization': self.get_object()})
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(serializer.data)


class GroupViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizationAdminOrReadOnly)
