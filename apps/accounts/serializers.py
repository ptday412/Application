from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

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