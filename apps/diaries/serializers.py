from rest_framework import serializers
from .models import Mood, Hashtag, Diary, DiaryImage
from django.db import transaction


class DiaryImageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryImage
        fields = ['image']


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


class DiaryImageSerializer(serializers.ModelSerializer):
    class Meta :
        model = DiaryImage
        fields='__all__'
        read_only_fields = ['diary',]


class DiaryWriteSerializer(serializers.ModelSerializer):
    moods = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Mood.objects.all()
    )
    hashtags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Hashtag.objects.all()
    )
    images = DiaryImageWriteSerializer(many=True)

    class Meta:
        model = Diary
        fields = ['ymd', 'title', 'content', 'moods', 'hashtags', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        hashtags = validated_data.pop('hashtags', None)  # 클라이언트가 보낸 hashtag 리스트
        request = self.context.get('request')

        diary = Diary.objects.create(user=request.user, **validated_data)
        diary.moods.set(moods)  # Many-to-many 관계 설정
        diary.hashtags.set(hashtags)  # Many-to-many 관계 설정

        if images:
            for image in images:
                DiaryImage.objects.create(diary=diary, **image)

        return diary

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)
        hashtags = validated_data.pop('hashtags', None)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        with transaction.atomic():
            if moods:
                instance.moods.clear()
                instance.moods.set(moods)
            if hashtags:
                instance.hashtags.clear()
                instance.hashtags.set(hashtags)
            if images:
                instance.images.all().delete()
                for image in images:
                    DiaryImage.objects.create(diary=instance, **image)

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