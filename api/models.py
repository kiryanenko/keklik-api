from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models


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


class Quiz(models.Model):
    title = models.CharField(max_length=300, db_index=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    rating = models.IntegerField(default=0, db_index=True)
    version_date = models.DateTimeField(auto_created=True)
    old_version = models.ForeignKey('Quiz', on_delete=models.CASCADE, null=True)


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    number = models.IntegerField(db_index=True)

    TYPE_CHOICES = (
        ('single', 'Single'),
        ('multi', 'Multi'),
        ('sequence', 'Sequence'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    question = models.TextField()
    answer = ArrayField(
        models.IntegerField()
    )
    time = models.TimeField(null=True)
    points = models.IntegerField()

    class Meta:
        unique_together = ('number', 'question')


class Variant(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    variant = models.CharField(max_length=300)

    class Meta:
        unique_together = ('variant', 'question')


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True, db_index=True)
