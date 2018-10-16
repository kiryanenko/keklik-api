from channels_api.bindings import ReadOnlyResourceBinding
from channels_api import mixins, detail_action, permissions

from api.models import Game, Player
from api.serializers.game import GameSerializer


class GameBinding(mixins.SubscribeModelMixin, ReadOnlyResourceBinding):
    model = Game
    stream = "games"
    serializer_class = GameSerializer
    queryset = Game.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    @detail_action()
    def join(self, pk, data=None, **kwargs):
        game = self.get_object(pk)
        Player.objects.create(game=game)
        return {}, 200

