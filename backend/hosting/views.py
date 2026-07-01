from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission
from .models import Event
from .serializers import EventSerializer


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the owner
        return obj.user == request.user


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.all()

    def get_permissions(self):
        # Anyone can view events
        if self.request.method == "GET":
            return [permissions.AllowAny()]

        # Only authenticated users can host(create) events
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    lookup_field = "event_id"
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        # Anyone can view a single event
        if self.request.method == "GET":
            return [permissions.AllowAny()]

        # Login required for update/delete
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]