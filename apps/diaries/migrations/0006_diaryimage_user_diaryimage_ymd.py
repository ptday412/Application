# Generated by Django 5.1.4 on 2024-12-15 09:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0005_alter_statistics_consolation_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='diaryimage',
            name='user',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='diaryimage',
            name='ymd',
            field=models.DateField(default='2024-10-10'),
            preserve_default=False,
        ),
    ]