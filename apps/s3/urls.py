from django.urls import path
from .views import call_lambda1


urlpatterns = [
    path('', call_lambda1),
]