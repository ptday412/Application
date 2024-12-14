from rest_framework import generics, permissions
from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
                            SignupSerializer,
                            OnboardingSerializer,
                            UserSerializer,
                        )
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import (
    RetrieveDestroyAPIView
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class CheckUsernameView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        username = request.data.get('username')
        
        if not username:
            return Response({"error": "username을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        is_exist = User.objects.filter(username=username).exists()

        if is_exist:
            return Response({"available": False, "message": "해당 유저네임이 이미 존재합니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"available": True, "message": "유저네임 설정 가능"}, status=status.HTTP_200_OK)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


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


class UserDetailDeleteView(RetrieveDestroyAPIView):
    permission_classes = [IsOwner]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'


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

@api_view(['PUT'])
def update_nickname(request, username):
    if username != request.user.username:
        return Response({"error": "본인 이외의 닉네임 변경 불가능"}, status=status.HTTP_400_BAD_REQUEST)
    new_nickname = request.data.get('nickname')
    if not new_nickname:
        return Response({"error": "닉네임 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, username=username)
    user.nickname = new_nickname
    user.save()
    return Response({"message": f"'{new_nickname}'으로 변경됨"}, status=status.HTTP_200_OK)