from rest_framework import serializers
from .models import Mood, Hashtag, Diary, DiaryImage
from django.db import transaction
from django.shortcuts import get_object_or_404


class DiaryImageReadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)  # 이미지 URL 반환

    class Meta:
        model = DiaryImage
        fields = ['image']  # 이미지 ID와 URL만 포함


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['name']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['name']


class DiaryWriteSerializer(serializers.ModelSerializer):
    moods = serializers.CharField(required=True)
    # hashtags = serializers.ListField(
    #     child=serializers.CharField(max_length=50),
    #     write_only=True
    # )
    hashtags = serializers.CharField(required=True)
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    class Meta:
        model = Diary
        fields = ['ymd', 'title', 'content', 'moods', 'hashtags', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        hashtags_data = validated_data.pop('hashtags', None)  # 클라이언트가 보낸 hashtag 리스트
        request = self.context.get('request')
        mood_id = Mood.objects.get(name=moods)
        diary = Diary.objects.create(user=request.user, moods=mood_id,  **validated_data)

        hashtag_list = hashtags_data.split(',')
        hashtags = []
        for hashtag in hashtag_list:
            name = hashtag.replace(' ', '')
            hashtag, created = Hashtag.objects.get_or_create(name=name)
            hashtags.append(hashtag)
        diary.hashtags.set(hashtags)  # Many-to-many 관계 설정

        if images:
            for image in images:
                DiaryImage.objects.create(diary=diary, image=image)
                pass

        return diary

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)
        mood_id = Mood.objects.get(name=moods)
        hashtags_data = validated_data.pop('hashtags', None)
        instance.ymd = validated_data.get('ymd', instance.ymd)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.moods = mood_id
        instance.save()

        with transaction.atomic():
            if hashtags_data:
                instance.hashtags.clear()
                hashtag_list = hashtags_data.split(',')
                hashtags = []
                for hashtag in hashtag_list:
                    name = hashtag.replace(' ', '')
                    hashtag, created = Hashtag.objects.get_or_create(name=name)
                    hashtags.append(hashtag)
                instance.hashtags.set(hashtags)
            if images:
                instance.images.all().delete()
                for image in images:
                    DiaryImage.objects.create(diary=instance, image=image)

        return instance


class AiDiaryWriteSerializer(serializers.ModelSerializer):
    moods = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Mood.objects.all()
    )
    hashtags = serializers.CharField(required=True)
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Diary
        fields = ['ymd', 'title', 'content', 'moods', 'hashtags', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        hashtags_data = validated_data.pop('hashtags', None)  # 클라이언트가 보낸 hashtag 리스트
        request = self.context.get('request')

        diary = Diary.objects.create(user=request.user, **validated_data)
        diary.moods.set(moods)  # Many-to-many 관계 설정

        hashtag_list = hashtags_data.split(',')
        hashtags = []
        for hashtag in hashtag_list:
            name = hashtag.replace(' ', '')
            hashtag, created = Hashtag.objects.get_or_create(name=name)
            hashtags.append(hashtag)
        diary.hashtags.set(hashtags)  # Many-to-many 관계 설정

        if images:
            for image in images:
                DiaryImage.objects.create(diary=diary, image=image)

        return diary

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)
        hashtags_data = validated_data.pop('hashtags', None)
        instance.ymd = validated_data.get('ymd', instance.ymd)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        with transaction.atomic():
            if moods:
                instance.moods.clear()
                instance.moods.set(moods)
            if hashtags_data:
                instance.hashtags.clear()
                hashtag_list = hashtags_data.split(',')
                hashtags = []
                for hashtag in hashtag_list:
                    name = hashtag.replace(' ', '')
                    hashtag, created = Hashtag.objects.get_or_create(name=name)
                    hashtags.append(hashtag)
                instance.hashtags.set(hashtags)
            if images:
                instance.images.all().delete()
                for image in images:
                    DiaryImage.objects.create(diary=instance, image=image)

        return instance


class DiaryReadSerializer(serializers.ModelSerializer):
    images = DiaryImageReadSerializer(many=True, read_only=True)
    moods = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        read_only=True,
    )
    hashtags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = Diary
        fields = ['id', 'ymd', 'title', 'content', 'moods', 'hashtags', 'images']