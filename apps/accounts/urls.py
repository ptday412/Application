from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('onboarding/', views.OnboardingView.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('<how>/logout/', views.logout), # 의도: how에 token입력 시 일반 로그아웃
    path('token/refresh/', TokenRefreshView.as_view()),
]