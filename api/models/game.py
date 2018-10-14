from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models

from api.models import Quiz, User, Question


class Game(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    pin = models.CharField(max_length=10, db_index=True)
    title = models.CharField(max_length=300)
    online = models.BooleanField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    STATE_CHOICES = (
        ('players_waiting', 'Ожидание игроков'),
        ('answering', 'Игроки отвечают на вопросы'),
        ('check', 'Показ правильного ответа'),
        ('finish', 'Финиш'),
    )
    state = models.CharField(max_length=15, choices=STATE_CHOICES, db_index=True)
    current_question = models.ForeignKey('GeneratedQuestion', on_delete=models.CASCADE, null=True, related_name='+')
    timer_on = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    finished_at = models.DateTimeField(null=True, db_index=True)

    @property
    def timer(self):
        if self.current_question is None:
            return None

        timer = self.current_question.question.timer
        if timer is None:
            return None

        return datetime.now() - self.updated_at - timer


class GeneratedQuestion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    variants_order = ArrayField(
        models.IntegerField(), help_text='ID вариантов. При создании новой игры варианты перемешиваются.'
    )

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
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
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