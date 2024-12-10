from rest_framework import serializers
from .models import Mood, Hashtag, Diary, DiaryImage
from django.db import transaction


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
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    def validate(self, data):
        # Images 검증
        images = data.get('images', [])
        if len(images) > 3:
            raise serializers.ValidationError("You can only upload up to 3 images.")

        return data

    class Meta:
        model = Diary
        fields = ['ymd', 'title', 'content', 'moods', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        mood_id = Mood.objects.get(name=moods)
        request = self.context.get('request')
        diary = Diary.objects.create(user=request.user, moods=mood_id,  **validated_data)

        if images:
            for image in images:
                DiaryImage.objects.create(diary=diary, image=image)

        return diary

    def update(self, instance, validated_data):
        images = validated_data.pop('images', instance.images)
        moods = validated_data.pop('moods', instance.moods)
        mood_id = Mood.objects.get(name=moods)
        instance.ymd = validated_data.get('ymd', instance.ymd)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.moods = mood_id
        instance.save()

        with transaction.atomic():
            if images:
                instance.images.all().delete()
                for image in images:
                    DiaryImage.objects.create(diary=instance, image=image)

        return instance


class AiDiaryWriteSerializer(serializers.ModelSerializer):
    moods = serializers.CharField(required=True)
    hashtags = serializers.CharField(required=True)
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Diary
        fields = ['ymd', 'title', 'content', 'moods', 'hashtags', 'images']

    def validate(self, data):
        # Hashtags 검증
        hashtags = data.get('hashtags', '')
        hashtag_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
        if len(hashtag_list) > 3:
            raise serializers.ValidationError("You can only add up to 3 hashtags.")

        # Images 검증
        images = data.get('images', [])
        if len(images) > 1:
            raise serializers.ValidationError("You can only upload up to 1 images.")

        return data

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        mood_id = Mood.objects.get(name=moods)
        hashtags_data = validated_data.pop('hashtags', None)  # 클라이언트가 보낸 hashtag 리스트
        request = self.context.get('request')
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

        return diary

    def update(self, instance, validated_data):
        images = validated_data.pop('images', instance.images)
        moods = validated_data.pop('moods', instance.moods)
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