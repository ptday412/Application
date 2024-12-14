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
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.content


class DiaryImage(models.Model):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="images"
        )
    username = models.CharField(max_length=150)
    image = models.TextField(blank=True, null=True)
    ai_analyze = models.TextField()


class Statistics(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="statistics"
    )
    ymd = models.DateField()
    emotions_summary = models.CharField(max_length=50) # 감정 요약
    consolation = models.CharField(max_length=100) # 위로의 말
    recommend_activities = models.TextField() # 추천활동
    recommend_reason = models.TextField() # 추천이유