import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()

from faker import Faker
from apps.accounts.models import User
from apps.diaries.models import Diary, Mood
from datetime import datetime, timedelta

fake = Faker()

# users = [User(username=fake.name(), password=fake.password()) for _ in range(10)]
# User.objects.bulk_create(users)

# 내 다이어리에 20개 추가하기(다른 날짜, mood 최대한 안겹치게)
today = datetime.now()
dates = [today - timedelta(days=i) for i in range(20)]
random_date = [date.strftime('%Y-%m-%d') for date in dates]
print(random_date)
random_moods = [mood for mood in Mood.objects.all()]
me = User.objects.get(pk=1)

diary = [Diary(ymd=random_date[_], content=fake.sentence(nb_words=3), user=me, moods=random_moods[_]) for _ in range(20)]
print(diary)
Diary.objects.bulk_create(diary)