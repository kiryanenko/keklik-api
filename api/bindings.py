from channels import Group
from channels_api import mixins, detail_action, permissions
from channels_api.bindings import ReadOnlyResourceBinding, ResourceBindingBase
from rest_framework.exceptions import PermissionDenied

from api.models import Game, Player
from api.serializers.game import GameSerializer, PlayerSerializer


class GroupMixin(object):
    def broadcast(self, action, pk=None, data=None, model=None):
        if model is None:
            model = self.model

        Group(self._group_name('join', pk)).send(self.encode(self.stream, {
            'action': action,
            'pk': pk,
            'data': data,
            'model': model.__name__
        }))


class GameBinding(GroupMixin, mixins.SubscribeModelMixin, ReadOnlyResourceBinding):
    model = Game
    stream = "games"
    serializer_class = GameSerializer
    queryset = Game.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    @detail_action()
    def join(self, pk, data=None, **kwargs):
        game = self.get_object_or_404(pk)
        player = game.join(self.user)

        self.broadcast('join', pk=pk, data=PlayerSerializer(player).data, model=Player)

        return GameSerializer(game).data, 200

    @detail_action()
    def next_question(self, pk, data=None, **kwargs):
        game = self.get_object_or_404(pk)

        if game.user != self.user:
            raise PermissionDenied()

        game.next_question()

        self.broadcast('next_question', pk=pk, data=GameSerializer(game).data, model=Player)

        return GameSerializer(game).data, 200
