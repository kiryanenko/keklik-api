from django.test import TestCase

from api.models import Game
from api.serializers.game import AnswerSerializer
from api.tests import ALL_FIXTURES


class SerializersTests(TestCase):
    fixtures = ALL_FIXTURES

    def test_answer_serializer(self):
        game = Game.objects.get(label='Last question')
        user = game.players.first().user
        answer = game.current_question.answer

        serializer = AnswerSerializer(game=game, user=user, data={
            'answer': answer,
            'question': game.current_question.id
        })

        valid = serializer.is_valid()
        self.assertTrue(valid, serializer.errors)

        player_answer = serializer.save()
        self.assertEqual(player_answer.answer, answer)
        self.assertEqual(player_answer.question, game.current_question)
