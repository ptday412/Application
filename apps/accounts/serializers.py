from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import Interest, Personality

User = get_user_model()

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, 
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
        )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
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
        # interest_list = [tag.strip() for tag in interests.split(',') if tag.strip()]
        if len(interests) > 3:
            raise serializers.ValidationError("You can only add up to 3 interests.")

        personalities = data.get('personalities', [])
        # personality_list = [tag.strip() for tag in personalities.split(',') if tag.strip()]
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