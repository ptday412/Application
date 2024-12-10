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
    interests = models.ForeignKey(
        Interest, on_delete=models.PROTECT, related_name="interest_by_user"
        )
    personalities = models.ForeignKey(
        Personality, on_delete=models.PROTECT, related_name="personality_by_user"
        )
    GENDER_CHOICE = (
            ('M', 'Man'),
            ('W', 'Woman'),
            ('O', 'Other'),
        )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    birth = models.DateField()
    nickname = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to="%Y/%m/%d", blank=True, null=True)

    def __str__(self):
        return self.username