from channels_api.bindings import ResourceBinding

from api.models import Game
from api.serializers.game import GameSerializer


class GameBinding(ResourceBinding):
    model = Game
    stream = "games"
    serializer_class = GameSerializer
    queryset = Game.objects.all()
