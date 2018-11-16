from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Game
from api.serializers.game import GameSerializer, CreateGameSerializer, PlayerSerializer
from api.utils.views import status_text, CustomGenericViewSet


class GameViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  CustomGenericViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filter_fields = ('state',)
    ordering_fields = ('id', 'created_at', 'title')
    ordering = ('-created_at', '-id')

    @swagger_auto_schema(
        request_body=CreateGameSerializer,
        responses={
            status.HTTP_201_CREATED: GameSerializer,
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN)
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = CreateGameSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PlayerSerializer(many=True),
            status.HTTP_404_NOT_FOUND: status_text(status.HTTP_404_NOT_FOUND)
        }
    )
    @action(detail=True)
    def rating(self, request, *args, **kwargs):
        game = self.get_object()
        return Response(PlayerSerializer(game.players_rating, many=True).data)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def my(self, request, *args, **kwargs):
        """ Созданные игры текущим пользователем (учителем). """
        games = self.get_user_games(request.user)
        return self.get_list_response(games)

    @swagger_auto_schema(operation_id='my_running_games')
    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='my/running'
    )
    def my_running(self, request, *args, **kwargs):
        """ Запущенные игры текущим пользователем (учителем). """
        games = self.get_user_games(request.user).exclude(state=Game.FINISH_STATE)
        return self.get_list_response(games)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def current_player(self, request, *args, **kwarg):
        """ Игры текущего игрока. """
        games = self.get_player_games(request.user)
        return self.get_list_response(games)

    @swagger_auto_schema(operation_id='current_player_running_games')
    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='current_player/running',
    )
    def current_player_running(self, request, *args, **kwarg):
        """ Незавершенные игры текущего игрока. """
        games = self.get_player_games(request.user).exclude(state=Game.FINISH_STATE)
        return self.get_list_response(games)

    def get_user_games(self, user):
        return self.filter_queryset(self.get_queryset().filter(user=user))

    def get_player_games(self, user):
        return self.filter_queryset(self.get_queryset().filter(players__user=user))


class MediaGameViewSet(GenericViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: 'Game_1__2018-11-02_22-43.xlsx',
            status.HTTP_404_NOT_FOUND: status_text(status.HTTP_404_NOT_FOUND)
        }
    )
    @action(detail=True)
    def report(self, *args, **kwargs):
        game = self.get_object()
        report = game.make_report()

        response = HttpResponse(
            report,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % game.report_filename

        return response
