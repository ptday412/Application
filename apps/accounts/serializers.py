from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import Interest, Personality
import random
import re

User = get_user_model()

# 정규표현식
regex = r'^(?=.*[A-Z])(?=.*[a-z])|(?=.*[A-Z])(?=.*\d)|(?=.*[A-Z])(?=.*[!@#$%^&*])|(?=.*[a-z])(?=.*\d)|(?=.*[a-z])(?=.*[!@#$%^&*])|(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{6,20}$'

# 검증 함수
def validate_password(password):
    return bool(re.match(regex, password))


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, 
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
        )
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, data):
        is_validate = validate_password(data['password'])
        if not is_validate:
            raise serializers.ValidationError('영문 대문자와 소문자, 숫자, 특수문자 중 2가지 이상 조합하여 6~20자로 입력해주세요.')
        return data
    
    def create(self, validated_data):
        names = ['성장마스터', '내면탐험가', '기록왕', '기록이', '끄적이', '메모쟁이', '자기분석러', '일기천재', '성장메이트', '새싹기록', '행복충전']
        selected_name = random.choice(names)
        user = User.objects.create_user(
            username = validated_data['username'],
            nickname = selected_name
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class OnboardingSerializer(serializers.ModelSerializer):
    interests = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Interest.objects.all()
    )
    personalities = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Personality.objects.all()
    )

    class Meta:
        model = User
        fields = ['interests', 'personalities']

    def validate(self, data):
        interests = data.get('interests', [])
        if len(interests) > 3:
            raise serializers.ValidationError("You can only add up to 3 interests.")

        personalities = data.get('personalities', [])
        if len(personalities) > 3:
            raise serializers.ValidationError("You can only add up to 3 personalities.")

        return data

    def update(self, instance, validated_data):
        interests_data = validated_data.pop('interests')
        personalities_data = validated_data.pop('personalities')

        if interests_data:
            instance.interests.clear()
            instance.interests.set(interests_data)
        if personalities_data:
            instance.personalities.clear()
            instance.personalities.set(personalities_data)

        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()
    personalities = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['interests', 'personalities', 'gender', 'birth', 'nickname', 'profile_picture']

    def get_interests(self, obj):
        return [interest.name for interest in obj.interests.all()]

    def get_personalities(self, obj):
        return [personality.name for personality in obj.personalities.all()]