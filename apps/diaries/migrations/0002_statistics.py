# Generated by Django 5.1.4 on 2024-12-13 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ymd', models.DateField()),
                ('emotions_summary', models.CharField(max_length=50)),
                ('consolation', models.CharField(max_length=100)),
                ('recommend_activities', models.TextField()),
                ('recommend_reason', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
