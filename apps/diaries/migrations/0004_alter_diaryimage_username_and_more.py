# Generated by Django 5.1.4 on 2024-12-14 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0003_diaryimage_username_alter_diaryimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diaryimage',
            name='username',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='consolation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='emotions_summary',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='recommend_activities',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='recommend_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
