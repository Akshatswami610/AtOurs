from django.urls import path
from .views import SupportView

urlpatterns = [
    path('', SupportView.as_view(), name='support'),
]