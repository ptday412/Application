from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Diary(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="diary_owner"
        )
    moods = models.ForeignKey(
        Mood, on_delete=models.PROTECT, related_name='diaries_by_mood'
        )
    hashtags = models.ManyToManyField(Hashtag, related_name='diaries_by_hashtag')
    ymd = models.DateTimeField()
    title = models.CharField(max_length=120)
    content = models.TextField()

    def __str__(self):
        return self.title


class DiaryImage(models.Model):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="images"
        )
    image = models.ImageField(upload_to="%Y/%m/%d", blank=True, null=True)
    ai_analyze = models.TextField()