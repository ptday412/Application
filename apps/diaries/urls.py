from django.urls import path
from .views import DiaryLCView, DiaryRUDView, AiDiaryCreateView, AiStatisticsLC


urlpatterns = [
    path('', DiaryLCView.as_view()),
    path('ai/', AiDiaryCreateView.as_view()),
    path('<int:pk>/', DiaryRUDView.as_view()),
    path('statistics/', AiStatisticsLC.as_view()),
]