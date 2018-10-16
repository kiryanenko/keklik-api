from datetime import datetime
from random import random

from django.contrib.postgres.fields import ArrayField
from django.db import models
from rest_framework.exceptions import APIException, ValidationError

from api.models import Quiz, User, Question


class GameManager(models.Manager):
    def new_game(self, quiz, title, online, user):
        game = self.create(quiz=quiz, title=title, online=online, user=user)

        for question in quiz.questions.all():
            GeneratedQuestion.objects.generate(game, question)

        return game


class Game(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    online = models.BooleanField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    STATE_CHOICES = (
        ('players_waiting', 'Ожидание игроков'),
        ('answering', 'Игроки отвечают на вопросы'),
        ('check', 'Показ правильного ответа'),
        ('finish', 'Финиш'),
    )
    state = models.CharField(max_length=15, choices=STATE_CHOICES, db_index=True, default='players_waiting')
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

    @property
    def timer(self):
        if self.current_question is None:
            return None

        timer = self.current_question.question.timer
        if timer is None:
            return None

        return datetime.now() - self.updated_at - timer

    def join(self, user):
        if self.state != 'players_waiting':
            raise ValidationError(detail='Game state is not "players_waiting".', code='not_players_waiting')

        player = Player.objects.get_or_create(game=self, user=user)
        self.save()
        return player


class GeneratedQuestionManager(models.Manager):
    def generate(self, game, question):
        variants_order = random.shuffle(map(lambda variant: variant.id, question.variants))
        return self.create(game=game, question=question, variants_order=variants_order)


class GeneratedQuestion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    variants_order = ArrayField(
        models.IntegerField(), help_text='ID вариантов. При создании новой игры варианты перемешиваются.'
    )

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


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, db_index=True)


class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE)
    answer = ArrayField(
        models.IntegerField(), help_text='ID правильных вариантов ответов.\n'
                                         'Для Single вопросов массив состоит из одного элемента.\n'
                                         'Для Sequence важен порядок.'
    )
    answered_at = models.DateTimeField(auto_now=True)
