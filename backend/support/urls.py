from django.urls import path
from .views import SupportViewSet

urlpatterns = [
    path('', SupportViewSet.as_view(), name='support'),
]