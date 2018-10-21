from django.test import TestCase

from api.models import Game
from api.tests import ALL_FIXTURES


class GameModelTest(TestCase):
    fixtures = ALL_FIXTURES

    def test_correct_answer_change_to_incorrect(self):
        game = Game.objects.get(label='Last question')
        player = game.players.first()
        correct_answer = game.current_question.answer

        player_answer = game.answer(player, correct_answer)
        self.assertTrue(player_answer.correct)

        incorrect_answer = [game.current_question.question.variants.get(variant='Incorrect').pk]

        player_answer = game.answer(player, incorrect_answer)
        self.assertFalse(player_answer.correct)

    def test_incorrect_answer_change_to_correct(self):
        game = Game.objects.get(label='Last question')
        player = game.players.first()
        incorrect_answer = [game.current_question.question.variants.get(variant='Incorrect').pk]

        player_answer = game.answer(player, incorrect_answer)
        self.assertFalse(player_answer.correct)

        correct_answer = game.current_question.answer

        player_answer = game.answer(player, correct_answer)
        self.assertTrue(player_answer.correct)
