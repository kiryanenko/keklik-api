from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api.models import Game
from api.serializers.game import GameSerializer
from api.serializers.quiz import QuizSerializer
from api.utils.views import status_text
from organization.models import Organization, Group, GroupMember
from organization.serializers import OrganizationDetailSerializer, GroupSerializer, AdminSerializer, AddAdminSerializer, \
    DeleteAdminSerializer, GroupMemberSerializer, AddQuizToOrganization, RemoveQuizFromOrganization


class IsOrganizationAdminOrReadOnly(permissions.BasePermission):
    @staticmethod
    def get_organization(obj):
        return obj if isinstance(obj, Organization) else obj.organization

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        organization = self.get_organization(obj)
        return organization.admins.filter(user=request.user).exists()


class IsOrganizationAdminOrTeacherOrReadOnly(IsOrganizationAdminOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            return True

        organization = self.get_organization(obj)
        return organization.groups.filter(members__user=request.user, members__role=GroupMember.TEACHER_ROLE).exists()


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationDetailSerializer
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
            status.HTTP_400_BAD_REQUEST: status_text(status.HTTP_400_BAD_REQUEST),
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

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def admin_at(self, request, *args, **kwargs):
        """ Список организаций, где текущий пользователь является админом. """
        organizations = self.get_queryset().filter(admins__user=request.user)
        return Response(self.get_serializer(organizations, many=True).data)

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

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: QuizSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Organization not found.'
        }
    )
    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticatedOrReadOnly, IsOrganizationAdminOrTeacherOrReadOnly)
    )
    def quizzes(self, *args, **kwargs):
        """ База викторин организации. """
        quizzes = self.get_object().quizzes.all().order_by('-id')
        return Response(QuizSerializer(quizzes, many=True).data)

    @swagger_auto_schema(
        request_body=AddQuizToOrganization,
        responses={
            status.HTTP_200_OK: QuizSerializer,
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN),
            status.HTTP_404_NOT_FOUND: 'Organization not found.'
        }
    )
    @quizzes.mapping.post
    def add_quiz(self, request, *args, **kwargs):
        """ Добавить викторину в базу викторин организации. """
        organization = self.get_object()
        serializer = AddQuizToOrganization(data=request.data, context={'organization': organization})
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        return Response(QuizSerializer(quiz).data)

    @swagger_auto_schema(request_body=RemoveQuizFromOrganization)
    @quizzes.mapping.delete
    def remove_quiz(self, request, *args, **kwargs):
        """ Удалить викторину из базы викторин организации. """
        organization = self.get_object()
        serializer = RemoveQuizFromOrganization(data=request.data, context={'organization': organization})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class GroupViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizationAdminOrReadOnly)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: GroupMemberSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Group not found.'
        }
    )
    @action(detail=True)
    def members(self, request, *args, **kwargs):
        """ Члены группы. """
        group = self.get_object()
        return Response(GroupMemberSerializer(group.members.all(), many=True).data)

    @swagger_auto_schema(
        request_body=GroupMemberSerializer,
        responses={
            status.HTTP_201_CREATED: GroupMemberSerializer,
            status.HTTP_400_BAD_REQUEST: status_text(status.HTTP_400_BAD_REQUEST),
            status.HTTP_404_NOT_FOUND: 'Group not found.'
        }
    )
    @members.mapping.post
    def add_member(self, request, *args, **kwargs):
        """ Добавление пользователя к группе. """
        serializer = GroupMemberSerializer(data=request.data, context={'group': self.get_object()})
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: GameSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Group not found.'
        }
    )
    @action(detail=True)
    def games(self, *args, **kwarg):
        """ История проведенных игр опубликованные в этой группе. """
        group = self.get_object()
        games = group.games.all().order_by('-id')
        return Response(GameSerializer(games, many=True).data)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: GameSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Group not found.'
        }
    )
    @action(detail=True, url_path='games/running')
    def running_games(self, *args, **kwarg):
        """ Запущенные игры в этой группе. """
        group = self.get_object()
        games = group.games.exclude(state=Game.FINISH_STATE).order_by('-id')
        return Response(GameSerializer(games, many=True).data)


class GroupMemberViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOrganizationAdminOrReadOnly)
