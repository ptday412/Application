# Generated by Django 5.1.4 on 2024-12-16 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0006_diaryimage_user_diaryimage_ymd'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diaryimage',
            name='ai_analyze',
        ),
        migrations.RemoveField(
            model_name='diaryimage',
            name='diary',
        ),
        migrations.RemoveField(
            model_name='diaryimage',
            name='user',
        ),
        migrations.AlterField(
            model_name='diaryimage',
            name='ymd',
            field=models.CharField(max_length=50),
        ),
    ]
