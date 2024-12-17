import os
import boto3
from config.settings.base import BASE_DIR
from rest_framework import serializers
from .models import Mood, Hashtag, Diary, DiaryImage, Statistics
from django.db import transaction
import datetime
import environ
from .image_analyze import genarate_ai_diary
from .ai_report import ai_report, report_emotion

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)


def generate_presigned_url(username, date, filename, expiration=3600):
    # S3 키 생성
    bucket_name = 'test-kilolog'
    region_name = 'ap-northeast-2'
    s3_key = f"{username}/{date}/{filename}"

    # S3 클라이언트 생성
    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
    )

    # URL 생성
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': s3_key},
        ExpiresIn=expiration
    )
    return presigned_url


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
    content = serializers.CharField(required=False)

    class Meta:
        model = Diary
        fields = ['ymd', 'content', 'moods']

    def create(self, validated_data):
        # 1일 1다이어리 제한
        ymd = validated_data.get('ymd')
        request = self.context.get('request')
        diary_exists = Diary.objects.filter(user=request.user, ymd=ymd).exists()
        if diary_exists:
            raise serializers.ValidationError('하루에 하나의 일기만 쓸 수 있습니다.')

        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        mood_id = Mood.objects.get(name=moods)
        diary = Diary.objects.create(user=request.user, moods=mood_id, **validated_data)

        return diary

    def update(self, instance, validated_data):
        request = self.context.get('request')
        # images = validated_data.pop('images', instance.images)
        moods = validated_data.pop('moods', instance.moods)
        mood_id = Mood.objects.get(name=moods)
        new_ymd = validated_data.get('ymd')
        if new_ymd != instance.ymd:
            is_exists = Diary.objects.filter(ymd=new_ymd, user=request.user).exists()
            if is_exists:
                raise serializers.ValidationError('해당 날짜의 일기가 이미 존재합니다.') 
        instance.ymd = validated_data.get('ymd', instance.ymd)
        instance.content = validated_data.get('content', instance.content)
        instance.moods = mood_id
        instance.save()

        return instance


class AiDiaryWriteSerializer(serializers.ModelSerializer):
    moods = serializers.CharField(required=True)
    hashtags = serializers.CharField(required=True)

    class Meta:
        model = Diary
        fields = ['ymd', 'moods', 'hashtags']

    def validate(self, data):
        # 1일 1다이어리 제한
        ymd = data.get('ymd')
        request = self.context.get('request')
        diary_exists = Diary.objects.filter(user=request.user, ymd=ymd).exists()
        if diary_exists:
            raise serializers.ValidationError('하루에 하나의 일기만 쓸 수 있습니다.')

        # Hashtags 검증
        hashtags = data.get('hashtags', '')
        hashtag_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
        if len(hashtag_list) > 3:
            raise serializers.ValidationError("You can only add up to 3 hashtags.")

        return data

    def create(self, validated_data):
        moods = validated_data.pop('moods', None)  # 클라이언트가 보낸 Mood 리스트
        mood_id = Mood.objects.get(name=moods)
        hashtags_data = validated_data.pop('hashtags', None)  # 클라이언트가 보낸 hashtag 리스트
        request = self.context.get('request')
        ymd = validated_data.get('ymd')
        is_exists = DiaryImage.objects.filter(ymd=str(ymd), username=request.user.username).exists()
        if not is_exists:
            raise serializers.ValidationError('분석할 사진이 저장되지 않았습니다.')
        images = DiaryImage.objects.filter(ymd=str(ymd), username=request.user.username).first()
        filename1 = images.image
        content = genarate_ai_diary(filename1, moods, hashtags_data)
        diary = Diary.objects.create(
            user=request.user, 
            moods=mood_id, 
            content=content, 
            **validated_data
        )

        hashtag_list = hashtags_data.split(',')
        hashtags = []
        for hashtag in hashtag_list:
            name = hashtag.replace(' ', '')
            hashtag, created = Hashtag.objects.get_or_create(name=name)
            hashtags.append(hashtag)
        diary.hashtags.set(hashtags)  # Many-to-many 관계 설정

        return diary

    def update(self, instance, validated_data):
        moods = validated_data.pop('moods', instance.moods)
        mood_id = Mood.objects.get(name=moods)
        hashtags_data = validated_data.pop('hashtags', None)
        new_ymd = validated_data.get('ymd')
        if new_ymd != instance.ymd:
            is_exists = Diary.objects.filter(ymd=new_ymd, user=request.user).exists()
            if is_exists:
                raise serializers.ValidationError('해당 날짜의 일기가 이미 존재합니다.') 
        instance.ymd = validated_data.get('ymd', instance.ymd)
        instance.content = validated_data.get('content', instance.content)
        instance.moods = mood_id
        instance.save()
        request = self.context.get('request')

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

        return instance


class DiaryReadSerializer(serializers.ModelSerializer):
    moods = serializers.SerializerMethodField()
    hashtags = HashtagSerializer(many=True, read_only=True)
    presigned_url = serializers.SerializerMethodField()

    class Meta:
        model = Diary
        fields = ['id', 'ymd', 'content', 'moods', 'hashtags', 'presigned_url']
    
    def get_moods(self, obj):
        return obj.moods.name if obj.moods else None
    
    def get_presigned_url(self, obj):
        request = self.context['request']
        username = request.user.username
        date = obj.ymd
        images = DiaryImage.objects.filter(ymd=obj.ymd, username=request.user.username)
        filename1 = images.values('image')
        filename2 = list(filename1)
        if filename2:
            filename3 = filename2[0]
            filename4 = filename3['image']
            preprocessed_filename = filename4.split('/')[-1]

            return generate_presigned_url(username, date, preprocessed_filename)
        return None


class AiStatisticCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ['emotions_summary', 'consolation', 'recommend_activities', 'recommend_reason']
    
    # def validate(self, data):
    #     request = self.context['request']
    #     # 메서드가 POST면
    #     if request.method == 'POST':
    #         # 현재 날짜가 일요일인지 확인
    #         today = datetime.date.today()
    #         if today.weekday() != 6:  # 6: 일요일 (0: 월요일, ..., 6: 일요일)
    #             raise serializers.ValidationError("통계는 일요일에만 생성 가능")
            
    #         ymd = self.validated_data['ymd']
    #         user = self.context['request'].user
    #         # 이미 그 주의 통계가 존재하는지
    #         is_exists = Statistics.objects.filter(user=user, ymd=ymd).exists()
    #         if is_exists:
    #             raise serializers.ValidationError('이미 이 주의 통계가 존재합니다.')
    #     return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        # context에서 request.user 가져오기
        validated_data['user'] = user  # user 필드에 request.user 저장
        ymd = datetime.date.today()
        validated_data['ymd'] = ymd
        all = ai_report()
        all_emotion = report_emotion(user.pk)
        weekly_mood = all_emotion.pop()
        max_mood = all_emotion.pop(0)
        emotion_list = [line.strip() for line in all_emotion[0].split('\n')]
        emotions_summary = emotion_list[0]
        consolation = emotion_list[1] + ' ' + emotion_list[2]


        validated_data['max_mood'] = max_mood
        validated_data['weekly_mood'] = weekly_mood
        validated_data['emotions_summary'] = emotions_summary
        validated_data['consolation'] = consolation
        validated_data['recommend_activities'] = all[0]
        validated_data['recommend_reason'] = all[1]
        return super().create(validated_data)


class AiStatisticReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = [
            'max_mood', 
            'weekly_mood', 
            'emotions_summary', 
            'consolation', 
            'recommend_activities', 
            'recommend_reason',
        ]