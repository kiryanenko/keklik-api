import random

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.dispatch import Signal
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api.models import Quiz, User, Question


class GameManager(models.Manager):
    def new_game(self, quiz, user, label='', online=False):
        game = self.create(quiz=quiz, label=label, online=online, user=user)

        for question in quiz.questions.all():
            GeneratedQuestion.objects.generate(game, question)

        return game


class Game(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    label = models.CharField(max_length=300, blank=True)
    online = models.BooleanField(default=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base_game = models.ForeignKey('Game', on_delete=models.CASCADE, null=True)

    PLAYERS_WAITING_STATE = 'players_waiting'
    ANSWERING_STATE = 'answering'
    CHECK_STATE = 'check'
    FINISH_STATE = 'finish'
    STATE_CHOICES = (
        (PLAYERS_WAITING_STATE, 'Ожидание игроков'),
        (ANSWERING_STATE, 'Игроки отвечают на вопросы'),
        (CHECK_STATE, 'Показ правильного ответа'),
        (FINISH_STATE, 'Финиш'),
    )
    state = models.CharField(max_length=15, choices=STATE_CHOICES, db_index=True, default=PLAYERS_WAITING_STATE)

    current_question = models.ForeignKey('GeneratedQuestion', on_delete=models.CASCADE, null=True, related_name='+')
    timer_on = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True,
                                      help_text='Дата обновляется при любых обновлениях снапшота игры: '
                                                'изменении модели, присоединение игрока, при новом ответе и т.д.')
    state_changed_at = models.DateTimeField(auto_now_add=True,
                                            help_text='Дата обновляется при изменении состояния `state` '
                                                      'и при изменении вопроса `current_question`.')
    finished_at = models.DateTimeField(null=True, db_index=True)

    objects = GameManager()

    joined_player = Signal(providing_args=['player'])
    question_changed = Signal()
    answered = Signal(providing_args=['answer'])
    finished = Signal()

    @property
    def timer(self):
        if self.current_question is None:
            return None

        timer = self.current_question.question.timer
        if timer is None:
            return None

        return timezone.now() - self.state_changed_at - timer

    def join(self, user):
        if self.state != self.PLAYERS_WAITING_STATE:
            raise ValidationError(detail='Game state is not "players_waiting".', code='not_players_waiting')

        player, created = Player.objects.get_or_create(game=self, user=user)
        if created:
            self.save()
            self.joined_player.send(self, player=player)
        return player

    def next_question(self):
        if self.state == self.FINISH_STATE:
            return self.current_question

        now = timezone.now()

        try:
            if self.current_question is None:
                self.current_question = self.generated_questions.first_question
            else:
                self.current_question = self.current_question.next
            self.state = self.ANSWERING_STATE
            self.state_changed_at = now
            self.current_question.started_at = now
            self.save()
            self.current_question.save()
            self.question_changed.send(self)

        except GeneratedQuestion.DoesNotExist:
            self.current_question = None
            self.state = self.FINISH_STATE
            self.state_changed_at = now
            self.save()
            self.finished.send(self)

        return self.current_question

    def answer(self, player, answer, question=None):
        if question is None:
            question = self.current_question

        correct = question.answer == answer
        points = self.count_points(question, correct)

        player_answer, created = Answer.objects.get_or_create(
            question=question,
            player=player,
            defaults={'answer': answer, 'correct': correct, 'points': points}
        )
        player.user.rating += points
        if not created:
            player_answer.correct = correct
            player.user.rating -= player_answer.points
            player_answer.points = points
            player_answer.save()
            player.user.save()

        self.save()

        self.answered.send(self, answer=player_answer)
        return player_answer

    @staticmethod
    def count_points(generated_question, correct=True):
        if not correct:
            return 0

        timer = generated_question.question.timer
        coefficient = (timezone.now() - generated_question.started_at) / timer if timer is not None else 1
        if coefficient < 0:
            coefficient = 0
        return generated_question.question.points + generated_question.question.points * coefficient


class GeneratedQuestionManager(models.Manager):
    def generate(self, game, question):
        variants_order = list(map(lambda variant: variant.pk, question.variants.all()))
        random.shuffle(variants_order)
        return self.create(game=game, question=question, variants_order=variants_order)

    @property
    def first_question(self):
        return self.get(question__number=1)


class GeneratedQuestion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='generated_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    variants_order = ArrayField(
        models.IntegerField(), help_text='ID вариантов. При создании новой игры варианты перемешиваются.'
    )
    started_at = models.DateTimeField(null=True)

    objects = GeneratedQuestionManager()

    @property
    def number(self):
        return self.question.number

    @property
    def type(self):
        return self.question.type

    @property
    def answer(self):
        return self.question.answer

    @property
    def timer(self):
        return self.question.timer

    @property
    def points(self):
        return self.question.points

    @property
    def next(self):
        return GeneratedQuestion.objects.get(game=self.game, question__number=self.number + 1)

    @property
    def variants(self):
        return list(map(lambda variant_id: self.question.variants.get(id=variant_id), self.variants_order))


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, db_index=True)


class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE, related_name='players_answers')
    answer = ArrayField(
        models.IntegerField(), help_text='ID правильных вариантов ответов.\n'
                                         'Для Single вопросов массив состоит из одного элемента.\n'
                                         'Для Sequence важен порядок.'
    )
    correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0, help_text='Начисленные очки за ответ.')
    answered_at = models.DateTimeField(auto_now=True)
