import os
import environ
import requests
from config.settings.base import BASE_DIR
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response


env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

# API URL
url = env('API_URL')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def call_lambda1(request):
    # 전송할 데이터
    data = {
        'username': request.user.username,
        'date': request.data.get('date'),
        'filename': request.data.get('filename')
    }

    # PUT 요청 보내기
    response = requests.put(url, json=data)

    # 응답 코드 및 본문 출력
    if response.status_code == 200:
        presigned_url = response.text
        return Response({presigned_url}, status=status.HTTP_200_OK)

    else:
        return Response({f"error occured: {response.status_code}"}, status=status.HTTP_400_BAD_REQUEST)