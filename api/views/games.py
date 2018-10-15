from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, filters, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Game
from api.serializers.game import GameSerializer, CreateGameSerializer
from api.utils.views import status_text


class GameViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticated,)

    filter_backends = (filters.OrderingFilter,)
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
