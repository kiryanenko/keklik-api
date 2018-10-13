from django.contrib.auth.models import AbstractUser
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
