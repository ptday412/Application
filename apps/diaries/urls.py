from django.urls import path
from .views import DiaryLCView, DiaryRUDView, AiDiaryCreateView, AiStatisticsLCView, AiStatisticsDetailView


urlpatterns = [
    path('', DiaryLCView.as_view()),
    path('ai/', AiDiaryCreateView.as_view()),
    path('<int:pk>/', DiaryRUDView.as_view()),
    path('statistics/', AiStatisticsLCView.as_view()),
    path('statistics/<int:pk>/', AiStatisticsDetailView.as_view()),
]