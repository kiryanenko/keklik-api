from rest_framework import mixins, permissions, filters
from rest_framework.viewsets import GenericViewSet

from api.models import Game
from api.serializers.game import GameSerializer


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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
