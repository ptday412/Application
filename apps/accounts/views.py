from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
                            SignupSerializer,
                            OnboardingSerializer,
                        )
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

@permission_classes([AllowAny])
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer


class OnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = OnboardingSerializer(instance=request.user, data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(OnboardingSerializer(user).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)