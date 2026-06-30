from django.urls import path
from .views import SupportView

urlpatterns = [
    path('help/', SupportView.as_view(), name='support'),
]