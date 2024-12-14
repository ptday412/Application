from rest_framework.permissions import IsAuthenticated
from .models import Diary, Statistics
from .serializers import (
    DiaryWriteSerializer, 
    DiaryReadSerializer, 
    AiDiaryWriteSerializer,
    AiStatisticSerializer,
)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView

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
        return Diary.objects.filter(user=user)


class DiaryRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DiaryReadSerializer
        return DiaryWriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Diary.objects.filter(user=user)


class AiStatisticsLC(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Statistics.objects.all()
    serializer_class = AiStatisticSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context