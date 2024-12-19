import datetime
from rest_framework.permissions import IsAuthenticated
from .models import Diary, Statistics
from .serializers import (
    DiaryWriteSerializer, 
    DiaryReadSerializer, 
    AiDiaryWriteSerializer,
    AiStatisticSerializer,
)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveAPIView
from datetime import datetime, date
from rest_framework.views import APIView
from rest_framework.response import Response

class AiDiaryCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AiDiaryWriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Diary.objects.filter(user=user)


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


def get_or_create_weekly_sentiments(request, year, month, weekstarts):
    today = date.today()
    for week_start in weekstarts:
        if week_start:
            try:
                date_obj = datetime.strptime(week_start, "%Y-%m-%d").date()
                print('Converted Date:', date_obj)

                is_exists = Statistics.objects.filter(user=request.user, week_start=date_obj).exists()
                if not is_exists and today > date_obj:
                    serializer = AiStatisticSerializer(data={'week_start': week_start}, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    print('>>>>>>>>>>>>>>> Saved:', serializer.data)
                else:
                    print('>>>>>>>>>>>>>>> Validation Failed:', serializer.errors)
            except Exception as e:
                print(f"Error processing week_start {week_start}: {e}")

    return Statistics.objects.filter(user=request.user, week_start__year=year, week_start__month=month)


class MonthlyStatisticsView(APIView):
    def get(self, request):
        year = int(request.query_params.get('year'))
        month = int(request.query_params.get('month'))
        
        # 데이터 조회 및 생성
        weekstarts=['2024-12-01', '2024-12-08', '2024-12-15', '2024-12-22', '2024-12-29']
        sentiments = get_or_create_weekly_sentiments(request, year, month, weekstarts)
        
        # 직렬화 및 응답 반환
        serializer = AiStatisticSerializer(sentiments, many=True)
        return Response(serializer.data)


# class AiStatisticsLCView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = AiStatisticSerializer

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context
    
#     def get_queryset(self):
#         year = int(self.request.query_params.get('year'))
#         month = int(self.request.query_params.get('month'))
#         user = self.request.user
#         queryset = Statistics.objects.filter(user=user)

#         if year and month:
#             today = date.today()

#             week_start_in_month = ['2024-12-01', '2024-12-08', '2024-12-15', '2024-12-22', '2024-12-29']
#             for week_start in week_start_in_month:
#                 if week_start:
#                     date_obj = datetime.strptime(week_start, "%Y-%m-%d").date()
#                     print('>>>>>>>>>>>>>>>', date_obj)
#                     is_exists = Statistics.objects.filter(week_start=date_obj).exists()
#                     if not is_exists and today > date_obj:
#                         # serializer_context = {'request': self.request}
#                         serializer = AiStatisticSerializer(data={'week_start': week_start})
#                         serializer.is_valid(raise_exception=True)
#                         serializer.save()
#             queryset = queryset.filter(ymd__year=year, ymd__month=month)  # 특정 년/월로 필터링
#         return queryset


class AiStatisticsDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AiStatisticSerializer

    def get_queryset(self):
        user = self.request.user
        return Statistics.objects.filter(user=user)