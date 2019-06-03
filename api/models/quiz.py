import json
import logging
import traceback
from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import User


logger = logging.getLogger(__name__)


class QuizManager(models.Manager):
    @transaction.atomic
    def create_quiz(self, questions=None, tags=None, **kwargs):
        quiz = self.create(**kwargs)

        if tags is not None:
            quiz.tags.add(*tags)

        if questions is not None:
            quiz.add_questions(*questions)

        quiz.save()
        return quiz


class Quiz(models.Model):
    class Meta:
        verbose_name = 'Викторина'
        verbose_name_plural = 'Викторины'

    title = models.CharField(verbose_name='Название', max_length=300, db_index=True)
    description = models.TextField(verbose_name='Описание', blank=True)
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', verbose_name='Теги')
    rating = models.IntegerField(verbose_name='Рейтинг', default=0, db_index=True)
    version_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата версии')
    old_version = models.ForeignKey('Quiz', verbose_name='Предыдущая версия', on_delete=models.CASCADE, null=True)

    objects = QuizManager()

    @transaction.atomic
    def update(self, title=None, description=None, questions=None, tags=None):
        if title is description is questions is tags is None:
            return self

        self.version_date = datetime.now()

        if title is not None:
            self.title = title
        if description is not None:
            self.description = description

        if tags is not None:
            self.tags.set(tags)

        if questions is not None:
            self.set_questions(*questions)

        self.save()
        return self

    def add_questions(self, *questions):
        for number, question_data in enumerate(questions, 1):
            variants = question_data.pop('variants', [])
            question = Question.objects.create(number=number, quiz=self, **question_data)

            # Сейчас ответ это порядковый номер в массиве вариантов его следует изменить на id варианта
            answer_dict = {}

            for var_index, variant_data in enumerate(variants, 1):
                variant = Variant.objects.create(question=question, **variant_data)

                if var_index in question.answer:
                    answer_dict[var_index] = variant.pk

            new_answer = list(map(lambda ans_key: answer_dict[ans_key], question.answer))
            question.answer = new_answer
            question.save()

    def set_questions(self, *questions):
        self.questions.all().delete()
        self.add_questions(*questions)

    @transaction.atomic
    def copy_to_user(self, user):
        quiz_clone = Quiz.objects.get(pk=self.pk)
        quiz_clone.pk = None
        quiz_clone.user = user
        quiz_clone.save()

        quiz_clone.tags.add(*self.tags.all())

        for question_src in self.questions.all():
            question_clone = Question.objects.get(pk=question_src.pk)
            question_clone.pk = None
            question_clone.quiz = quiz_clone
            question_clone.save()

            answer_dict = {}

            for variant_src in question_src.variants.all():
                variant_clone = Variant.objects.get(pk=variant_src.pk)
                variant_clone.pk = None
                variant_clone.question = question_clone
                variant_clone.save()

                if variant_src.pk in question_src.answer:
                    answer_dict[variant_src.pk] = variant_clone.pk

            question_clone.answer = list(map(lambda ans_key: answer_dict[ans_key], question_src.answer))
            question_clone.save()

        return quiz_clone

    @staticmethod
    @receiver(post_save, sender=User)
    def add_default_quizzes(sender, instance, created, **kwargs):
        if created:
            try:
                with open('api/fixtures/default_quizzes.json', 'r', encoding='utf-8') as fh:
                    quizzes_data = json.load(fh)
                    for quiz_data in quizzes_data:
                        try:
                            tags_data = quiz_data.pop('tags')
                            tags = Tag.objects.get_or_create_tags(tags_data)
                            Quiz.objects.create_quiz(user=instance, tags=tags, **quiz_data)
                        except:
                            logger.error('Error at adding default quiz:\n' + quiz_data)
                            logger.error(traceback.format_exc())
            except:
                logger.error('Error at adding default quizzes.')
                logger.error(traceback.format_exc())

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name='Викторина', on_delete=models.CASCADE, related_name='questions')
    number = models.SmallIntegerField(verbose_name='Номер вопроса',
                                      help_text='Номер вопроса, начиная с 1.\n'
                                                'Соответствует порядковому номеру в массиве.',
                                      db_index=True)

    TYPE_CHOICES = (
        ('single', 'Single - один верный ответ'),
        ('multi', 'Multi - несколько верных ответов'),
        ('sequence', 'Sequence - правильная последовательность'),
    )
    type = models.CharField(choices=TYPE_CHOICES, verbose_name='Тип вопроса', max_length=10)

    question = models.TextField(verbose_name='Текст вопроса')
    answer = ArrayField(
        models.IntegerField(), verbose_name='ID правильных вариантов ответов',
        help_text='Для Single вопросов массив состоит из одного элемента.\n'
                  'Для Sequence важен порядок.\n'
                  'При создании и изменении викторины указывать порядковый номер '
                  'в массиве вариантов (номер начинается с 1).'
    )
    timer = models.DurationField(null=True, verbose_name='Таймер', help_text='Таймер. Null означает, что таймера нет.')
    points = models.IntegerField(verbose_name='Очки за правильный ответ')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        unique_together = ('quiz', 'number')
        ordering = ('quiz', 'number')

    @property
    def answer_str(self):
        try:
            answer = list(map(lambda ans: Variant.objects.get(pk=ans).variant, self.answer))
            return '; '.join(answer)
        except Variant.DoesNotExist:
            return 'Variant does not exist.'

    def __str__(self):
        return '{}. {}'.format(self.number, self.question)


class Variant(models.Model):
    question = models.ForeignKey(Question, verbose_name='Вопрос', on_delete=models.CASCADE, related_name='variants')
    variant = models.CharField(verbose_name='Вариант', max_length=300)

    class Meta:
        verbose_name = 'Вариант'
        verbose_name_plural = 'Варианты'
        unique_together = ('variant', 'question')
        ordering = ('id',)

    def __str__(self):
        return self.variant


class TagManager(models.Manager):
    def get_or_create_tags(self, tags):
        return tuple(map(lambda tag: self.get_or_create(tag=tag)[0], tags))


class Tag(models.Model):
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    tag = models.CharField(verbose_name='Тег', max_length=50, unique=True, db_index=True)

    objects = TagManager()

    def __str__(self):
        return self.tag
