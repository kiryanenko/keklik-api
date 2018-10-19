from channels.test import ChannelTestCase, WSClient

from api.bindings import GameBinding
from api.models import Game, User
from api.tests.utils import ALL_FIXTURES


class BindingsTests(ChannelTestCase):
    fixtures = ALL_FIXTURES

    def test_join_subscription(self):
        game = Game.objects.first()

        client = WSClient()
        client.join_group(GameBinding.group_name(GameBinding.JOIN_SUB, game.pk))

        user = User.objects.get(username='free_user')
        game.join(user)

        received = client.receive()
        self.assertIsNotNone(received)
