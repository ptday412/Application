from rest_framework import generics
from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
                            SignupSerializer,
                            OnboardingSerializer,
                        )
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request, how):
    login_ways = ['token', 'kakao']
    if how not in login_ways:
        return Response({'error': how + '의 url은 지원하고 있지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if how == 'token':
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"message": "refresh token 필요"}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh)
        token.blacklist()
        return Response({'message': '토큰 로그아웃 성공'}, status=status.HTTP_200_OK)
    if how == 'kakao':
        pass