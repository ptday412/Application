from django.urls import path
from .views import DiaryLCView, DiaryRUDView, AiDiaryCreateView, MonthlyStatisticsView, AiStatisticsDetailView


urlpatterns = [
    path('', DiaryLCView.as_view()),
    path('ai/', AiDiaryCreateView.as_view()),
    path('<int:pk>/', DiaryRUDView.as_view()),
    path('statistics/', MonthlyStatisticsView.as_view()),
    path('statistics/<int:pk>/', AiStatisticsDetailView.as_view()),
]