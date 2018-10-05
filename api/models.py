from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    phone = models.CharField(max_length=30, blank=True)
    patronymic = models.CharField(max_length=50, blank=True)

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    birth_date = models.DateField(null=True)
    rating = models.IntegerField(default=0)

    @property
    def token(self):
        token, created = Token.objects.get_or_create(user=self)
        return token.key


class QuizManager(models.Manager):
    def create_quiz(self, questions=None, tags=None, **kwargs):
        if questions is None:
            questions = []
        if tags is None:
            tags = []
        quiz = self.create(**kwargs)

        for tag_data in tags:
            tag = Tag.objects.get_or_create(tag=tag_data)
            quiz.tags.add(tag)

        number = 1
        for question_data in questions:
            variants = question_data.pop('variants', [])
            question = Question.objects.create(number=number, quiz=quiz, **question_data)
            for variant_data in variants:
                Variant.objects.create(question=question, **variant_data)
            number += 1

        return quiz


class Quiz(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    rating = models.IntegerField(default=0, db_index=True)
    version_date = models.DateTimeField(auto_now_add=True)
    old_version = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True)

    objects = QuizManager()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    number = models.IntegerField(db_index=True, help_text='Номер вопроса, начиная с 1.\n'
                                                          'Соответствует порядковому номеру в массиве.')

    TYPE_CHOICES = (
        ('single', 'Single - один верный ответ'),
        ('multi', 'Multi - несколько верных ответов'),
        ('sequence', 'Sequence - правильная последовательность'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, help_text='Single - один верный ответ;\n'
                                                                           'Multi - несколько верных ответов;\n'
                                                                           'Sequence - правильная последовательность.')

    question = models.TextField(help_text='Текст вопроса.')
    answer = ArrayField(
        models.IntegerField(), help_text='ID правильных вариантов ответов.\n'
                                         'Для Single вопросов массив состоит из одного элемента.\n'
                                         'Для Sequence важен порядок.'
    )
    time = models.TimeField(null=True, help_text='Таймер. Null означает, что таймера нет.')
    points = models.IntegerField(help_text='Очки за правильный ответ')

    class Meta:
        unique_together = ('quiz', 'number')
        ordering = ('quiz', 'number')


class Variant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='variants')
    variant = models.CharField(max_length=300)

    class Meta:
        unique_together = ('variant', 'question')


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True, db_index=True)
