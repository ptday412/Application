from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Diary(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="diary_owner"
        )
    created_at = models.DateTimeField()
    title = models.CharField(max_length=120)
    content = models.TextField()


class DiaryImage(models.Model):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="diary_images"
        )
    img = models.ImageField(upload_to="%Y/%m/%d", blank=True, null=True)
    # ai_analyze = models.CharField()


class Mood(models.Model):
    name = models.CharField(max_length=50)


class DiaryMood(models.Model):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="diary_moods"
        )
    mood = models.ForeignKey(
        Mood, on_delete=models.CASCADE, related_name="diaries_by_mood"
        )


class Hashtag(models.Model):
    name = models.CharField(max_length=50)


class DiaryHashtag(models.Model):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="diary_hashtags"
        )
    hashtag = models.ForeignKey(
        Hashtag, on_delete=models.CASCADE, related_name="diaries_by_hashtag"
        )