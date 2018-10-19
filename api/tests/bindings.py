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
        self.assertEqual(received['stream'], GameBinding.stream)
        self.assertEqual(received['payload']['action'], GameBinding.JOIN_SUB)
        self.assertEqual(received['payload']['pk'], game.pk)
        self.assertEqual(received['payload']['data']['user']['username'], user.username)

    def test_next_question_subscription(self):
        game = Game.objects.first()

        client = WSClient()
        client.join_group(GameBinding.group_name(GameBinding.NEXT_QUESTION_SUB, game.pk))

        # Start game
        game.next_question()

        received = client.receive()
        self.assertIsNotNone(received)
        self.assertEqual(received['stream'], GameBinding.stream)
        self.assertEqual(received['payload']['action'], GameBinding.NEXT_QUESTION_SUB)
        self.assertEqual(received['payload']['pk'], game.pk)
        self.assertEqual(received['payload']['data']['id'], game.pk)

        # Next question
        game.next_question()

        received = client.receive()
        self.assertIsNotNone(received)
        self.assertEqual(received['stream'], GameBinding.stream)
        self.assertEqual(received['payload']['action'], GameBinding.NEXT_QUESTION_SUB)
        self.assertEqual(received['payload']['pk'], game.pk)
        self.assertEqual(received['payload']['data']['id'], game.pk)
