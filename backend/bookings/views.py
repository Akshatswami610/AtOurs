from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from hosting.models import Event
from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingDetailView(generics.RetrieveAPIView):

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )


class EventAttendeesView(APIView):
    """
    Bookings for a single event, scoped to that event's host — not the
    ticket buyer. Used by the hosting page to show "who booked my event".
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if event.user_id != request.user.id:
            return Response(
                {"error": "You do not have permission to view attendees for this event."},
                status=status.HTTP_403_FORBIDDEN,
            )

        bookings = Booking.objects.filter(event=event).order_by("-booked_at")

        serializer = BookingSerializer(bookings, many=True)

        return Response(serializer.data)