import datetime
from rest_framework.permissions import IsAuthenticated
from .models import Diary, Statistics, DiaryImage
from .serializers import (
    DiaryWriteSerializer, 
    DiaryReadSerializer, 
    AiDiaryWriteSerializer,
    AiStatisticSerializer,
)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveAPIView
from datetime import datetime, date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger("diaries.views")

class AiDiaryCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AiDiaryWriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Diary.objects.filter(user=user)
    
    def perform_create(self, serializer):
        try:
            # 객체 저장 시도
            serializer.save()
            logger.info("Successfully created an object.")
        except Exception as e:
            # 예외 발생 시 로그 기록
            logger.error(f"Error occurred while creating an object: {str(e)}")
            raise ValidationError({"detail": f"An error occurred: {str(e)}"})



class DiaryLCView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DiaryReadSerializer
        return DiaryWriteSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Diary.objects.filter(user=user)
        year = self.request.query_params.get('year')  # 쿼리 파라미터로 'year' 값을 가져옴
        month = self.request.query_params.get('month')  # 쿼리 파라미터로 'month' 값을 가져옴
        if year and month:
            queryset = queryset.filter(ymd__year=year, ymd__month=month)  # 특정 년/월로 필터링
        return queryset


class DiaryRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DiaryReadSerializer
        return DiaryWriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Diary.objects.filter(user=user)
    
    def perform_destroy(self, instance):
        related_images = DiaryImage.objects.filter(username=instance.user.username, ymd=instance.ymd)
        related_images.delete()
        instance.delete()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



def get_or_create_weekly_sentiments(request, year, month, weeks):
    today = date.today()

    if weeks:
        week_list = [days.strip() for days in weeks.split(',')]
        for week in week_list:
                print('>>>>>>>>>>>>>week', week)
                try:
                    week_start, week_end = week.split('@')
                    start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
                    end_date = datetime.strptime(week_end, "%Y-%m-%d").date()

                    is_diary_exists = Diary.objects.filter(user=request.user, ymd__range=(start_date, end_date)).exists()
                    is_exists = Statistics.objects.filter(user=request.user, week_start=start_date).exists()

                    if is_diary_exists and not is_exists and today > start_date and today > end_date:
                        serializer = AiStatisticSerializer(context={'request': request}, data={'week_start': week_start, 'week_end': week_end})
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                        else:
                            print('>>>>>>>>>>>>>>> Validation Failed:', serializer.errors)
                except Exception as e:
                    print(f"Error processing week_start {week_start}: {e}")

    return Statistics.objects.filter(user=request.user, week_start__year=year, week_start__month=month)


class MonthlyStatisticsView(APIView):
    def get(self, request):
        year = int(request.query_params.get('year'))
        month = int(request.query_params.get('month'))
        basedates = request.query_params.get('basedate')

        # 데이터 조회 및 생성
        sentiments = get_or_create_weekly_sentiments(request, year, month, basedates)
        
        # 직렬화 및 응답 반환
        serializer = AiStatisticSerializer(sentiments, many=True)
        return Response(serializer.data)


class AiStatisticsDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AiStatisticSerializer

    def get_queryset(self):
        user = self.request.user
        return Statistics.objects.filter(user=user)