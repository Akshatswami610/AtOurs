from rest_framework import generics, permissions
from .models import Support
from .serializers import SupportSerializer

class SupportView(generics.CreateAPIView):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    permission_classes = [permissions.AllowAny]