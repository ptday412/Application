from django.db import models
from django.contrib.auth.models import AbstractUser


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Personality(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    interests = models.ManyToManyField(
        Interest, related_name="interest_by_user", blank=True
        )
    personalities = models.ManyToManyField(
        Personality, related_name="personality_by_user", blank=True
        )
    GENDER_CHOICE = (
            ('M', 'Man'),
            ('W', 'Woman'),
            ('O', 'Other'),
        )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE, blank=True, null=True)
    birth = models.DateField(blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="%Y/%m/%d", blank=True, null=True)

    def __str__(self):
        return self.username