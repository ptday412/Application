# Generated by Django 5.1.4 on 2024-12-16 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0008_alter_diary_ymd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diaryimage',
            name='ymd',
            field=models.DateField(),
        ),
    ]