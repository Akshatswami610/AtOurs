from rest_framework import viewsets, permissions
from .models import Support
from .serializers import SupportSerializer

class SupportViewSet(viewsets.ModelViewSet):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    permission_classes = [permissions.AllowAny]