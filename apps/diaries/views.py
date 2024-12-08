from rest_framework.permissions import IsAuthenticated
from .models import Diary
from .serializers import DiaryWriteSerializer, DiaryReadSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


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