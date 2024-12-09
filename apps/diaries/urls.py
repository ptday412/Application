from django.urls import path
from .views import DiaryLCView, DiaryRUDView


urlpatterns = [
    path('', DiaryLCView.as_view()),
    path('<int:pk>/', DiaryRUDView.as_view()),
]