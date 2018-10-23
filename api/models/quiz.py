from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models

from api.models import User


class QuizManager(models.Manager):
    def create_quiz(self, questions=None, tags=None, **kwargs):
        quiz = self.create(**kwargs)

        if tags is not None:
            quiz.tags.add(*tags)

        if questions is not None:
            quiz.add_questions(*questions)

        quiz.save()
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

    def update(self, title=None, description=None,  questions=None, tags=None):
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


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    number = models.SmallIntegerField(db_index=True, help_text='Номер вопроса, начиная с 1.\n'
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
                                         'Для Sequence важен порядок.\n'
                                         'При создании и изменении викторины указывать порядковый номер '
                                         'в массиве вариантов (номер начинается с 1).'
    )
    timer = models.DurationField(null=True, help_text='Таймер. Null означает, что таймера нет.')
    points = models.IntegerField(help_text='Очки за правильный ответ')

    class Meta:
        unique_together = ('quiz', 'number')
        ordering = ('quiz', 'number')


class Variant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='variants')
    variant = models.CharField(max_length=300)

    class Meta:
        unique_together = ('variant', 'question')


class TagManager(models.Manager):
    def get_or_create_tags(self, tags):
        return tuple(map(lambda tag: self.get_or_create(tag=tag)[0], tags))


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True, db_index=True)

    objects = TagManager()
