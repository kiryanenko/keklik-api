from django.test import TestCase

from api.models import Game, User
from api.tests import ALL_FIXTURES


class GameModelTest(TestCase):
    fixtures = ALL_FIXTURES

    def test_join(self):
        game = Game.objects.get(label='new_game')
        user1 = User.objects.get(username='free_user')

        player = game.join(user1)
        self.assertEqual(player.user, user1)
        self.assertEqual(player.game, game)

        user2 = User.objects.get(username='free_user2')

        player = game.join(user2)
        self.assertEqual(game.players.count(), 2)
        self.assertEqual(player.user, user2)
        self.assertEqual(player.game, game)

    def test_correct_answer_change_to_incorrect(self):
        game = Game.objects.get(label='Last question')
        player = game.players.first()
        correct_answer = game.current_question.answer

        player_answer = game.answer(player, correct_answer)
        self.assertTrue(player_answer.correct)
        self.assertEqual(player_answer.answer, correct_answer)

        incorrect_answer = [game.current_question.question.variants.get(variant='Incorrect').pk]

        player_answer = game.answer(player, incorrect_answer)
        self.assertFalse(player_answer.correct)
        self.assertEqual(player_answer.answer, incorrect_answer)

    def test_incorrect_answer_change_to_correct(self):
        game = Game.objects.get(label='Last question')
        player = game.players.first()
        incorrect_answer = [game.current_question.question.variants.get(variant='Incorrect').pk]

        player_answer = game.answer(player, incorrect_answer)
        self.assertFalse(player_answer.correct)
        self.assertEqual(player_answer.answer, incorrect_answer)

        correct_answer = game.current_question.answer

        player_answer = game.answer(player, correct_answer)
        self.assertTrue(player_answer.correct)
        self.assertEqual(player_answer.answer, correct_answer)
