from rest_framework.permissions import IsAuthenticated
from .models import Diary, Statistics
from .serializers import (
    DiaryWriteSerializer, 
    DiaryReadSerializer, 
    AiDiaryWriteSerializer,
    AiStatisticCreateSerializer,
    AiStatisticReadSerializer,
)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveAPIView

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


class AiStatisticsLCView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return AiStatisticReadSerializer
        return AiStatisticCreateSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Statistics.objects.filter(user=user)


class AiStatisticsDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AiStatisticReadSerializer

    def get_queryset(self):
        user = self.request.user
        return Statistics.objects.filter(user=user)