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
        self.assertIsNotNone(received['payload']['data']['current_question'])

        # Next question
        game.next_question()

        received = client.receive()
        self.assertIsNotNone(received)
        self.assertEqual(received['stream'], GameBinding.stream)
        self.assertEqual(received['payload']['action'], GameBinding.NEXT_QUESTION_SUB)
        self.assertEqual(received['payload']['pk'], game.pk)
        self.assertEqual(received['payload']['data']['id'], game.pk)
        self.assertIsNotNone(received['payload']['data']['current_question'])

    def test_finish_subscription(self):
        game = Game.objects.get(label='Last question')

        client = WSClient()
        client.join_group(GameBinding.group_name(GameBinding.FINISH_SUB, game.pk))

        # Finish game
        game.next_question()

        received = client.receive()
        self.assertIsNotNone(received)
        self.assertEqual(received['stream'], GameBinding.stream)
        self.assertEqual(received['payload']['action'], GameBinding.FINISH_SUB)
        self.assertEqual(received['payload']['pk'], game.pk)
        self.assertEqual(received['payload']['data']['id'], game.pk)

    def test_answer_subscription(self):
        game = Game.objects.get(label='Last question')
        player = game.players.first()
        answer = game.current_question.answer

        client = WSClient()
        client.join_group(GameBinding.group_name(GameBinding.ANSWER_SUB, game.pk))

        game.answer(player, answer)

        received = client.receive()
        self.assertIsNotNone(received)
        self.assertEqual(received['stream'], GameBinding.stream)
        self.assertEqual(received['payload']['action'], GameBinding.ANSWER_SUB)
        self.assertEqual(received['payload']['pk'], game.pk)
        self.assertEqual(received['payload']['data']['answer'][0]['id'], answer[0])
