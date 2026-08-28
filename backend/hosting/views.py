from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Event, SavedEvent
from .serializers import EventSerializer, SavedEventSerializer


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
        queryset = Event.objects.all()

        # Optional host filter used by profile pages to show only events
        # created by a specific host.
        host_id = self.request.query_params.get("host_id")

        if host_id is not None:
            try:
                queryset = queryset.filter(user_id=int(host_id))
            except (TypeError, ValueError):
                queryset = queryset.none()

        # Opt-in filter used by the hosting/management page. Without a
        # "mine" param this stays the public, unauthenticated-friendly
        # listing that home.html relies on for browsing all events.
        mine = self.request.query_params.get("mine")

        if str(mine).lower() in ("1", "true", "yes"):
            if self.request.user and self.request.user.is_authenticated:
                queryset = queryset.filter(user=self.request.user)
            else:
                # Someone asked for "my events" without being logged in —
                # return nothing rather than silently showing everyone's.
                queryset = queryset.none()

        return queryset

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

# --------------------------------------------------
# SAVE EVENT
# --------------------------------------------------

class SaveEventView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):

        try:
            event = Event.objects.get(event_id=event_id)

        except Event.DoesNotExist:

            return Response(
                {
                    "error": "Event not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        saved_event, created = SavedEvent.objects.get_or_create(
            user=request.user,
            event=event
        )

        if not created:

            return Response(
                {
                    "message": "Event already saved."
                },
                status=status.HTTP_200_OK
            )

        serializer = SavedEventSerializer(saved_event)

        return Response(
            {
                "message": "Event saved successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


# --------------------------------------------------
# REMOVE SAVED EVENT
# --------------------------------------------------

class RemoveSavedEventView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, event_id):

        try:

            saved_event = SavedEvent.objects.get(
                user=request.user,
                event__event_id=event_id
            )

        except SavedEvent.DoesNotExist:

            return Response(
                {
                    "error": "Saved event not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        saved_event.delete()

        return Response(
            {
                "message": "Event removed from saved list."
            },
            status=status.HTTP_200_OK
        )


# --------------------------------------------------
# GET SAVED EVENTS
# --------------------------------------------------

class SavedEventListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        saved_events = SavedEvent.objects.filter(
            user=request.user
        ).select_related(
            "event"
        ).order_by(
            "-created_at"
        )

        serializer = SavedEventSerializer(
            saved_events,
            many=True
        )

        return Response(serializer.data)