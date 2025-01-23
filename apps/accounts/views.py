from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from config.settings.base import BASE_DIR
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
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging
from django.shortcuts import redirect
import requests, environ, os, hashlib
from django.db.utils import IntegrityError

logger = logging.getLogger("accounts.views")

User = get_user_model()

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

@permission_classes([AllowAny])
class CheckUsernameView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        username = request.query_params.get('username')
        
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

    def perform_create(self, serializer):
        try:
            # 객체 저장 시도
            serializer.save()
            logger.info("Successfully created an object.")
        except Exception as e:
            # 예외 발생 시 로그 기록
            logger.error(f"Error occurred while creating an object: {str(e)}")
            raise ValidationError({"detail": f"An error occurred: {str(e)}"})

@api_view(['GET'])
@permission_classes([AllowAny])
def kakaoLoginLogic(request):
    _restApiKey = env('KAKAO_REST_API_KEY')
    _redirectUrl = settings.BASE_URL+'api/accounts/kakao/login/redirect/'
    _url = f'https://kauth.kakao.com/oauth/authorize?client_id={_restApiKey}&redirect_uri={_redirectUrl}&response_type=code'
    return redirect(_url)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def kakaoLoginLogicRedirect(request):
    _qs = request.GET.get('code')
    if not _qs:
            return Response({"error": "인증 코드가 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

    _restApiKey = env('KAKAO_REST_API_KEY')
    _redirect_uri = settings.BASE_URL+'api/accounts/kakao/login/redirect/'
    _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={_restApiKey}&redirect_uri={_redirect_uri}&code={_qs}'
    _res = requests.post(_url)
    _result = _res.json()
    error = _result.get("error")

    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    access_token = request.data.get('access_token')
    print('>>>>>>>>>>>>>>>>>>>', access_token)
    profile_request = requests.get("https://kapi.kakao.com/v2/user/me",
                                    headers={"Authorization": f"Bearer {access_token}"})
    profile_data = profile_request.json()

    # 사용자 계정 정보 유무 확인
    kakao_account = profile_data.get("kakao_account")
    if not kakao_account:
        return Response({"error": "등록하려면 카카오 계정정보가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 카카오 ID와 이메일을 추출
    kakao_id = str(profile_data.get("id"))

    # 카카오 ID로부터 비밀번호를 생성하기 위한 해시를 생성
    hash_object = hashlib.sha256(kakao_id.encode())
    password_hash = hash_object.hexdigest()

    try:
        user, created = User.objects.get_or_create(username=kakao_id, password=password_hash)

        # 새로운 사용자가 생성되었다면 비밀번호를 설정 저장
        if created:
            user.set_password(password_hash)
            user.save()
    except IntegrityError:
            return Response({"error": "해당 username을 가진 사용자가 이미 있습니다."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return e

    refresh = RefreshToken.for_user(user)
    return Response({'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)}, status=status.HTTP_200_OK)


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
def logout(request):
    refresh = request.data.get("refresh")
    if not refresh:
        return Response({"message": "refresh token 필요"}, status=status.HTTP_400_BAD_REQUEST)
    token = RefreshToken(refresh)
    token.blacklist()
    return Response({'message': '토큰 로그아웃 성공'}, status=status.HTTP_200_OK)

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