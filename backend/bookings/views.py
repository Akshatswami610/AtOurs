from decimal import Decimal
import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from hosting.models import Event
from .models import Booking
from .serializers import BookingSerializer
from razorpay.errors import SignatureVerificationError

client = razorpay.Client(
    auth=( settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET )
)


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).order_by("-booked_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class EventAttendeesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.user != request.user:
            return Response(
                {"error": "You don't have permission."},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter( event=event, payment_status="paid", booking_status="confirmed" ).order_by("-booked_at")
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(pk=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if booking.booking_status == "cancelled":
            return Response({"message": "Booking already cancelled."})

        booking.booking_status = "cancelled"

        if booking.payment_status == "paid":
            booking.payment_status = "refunded"  # or keep "paid" if refunds aren't implemented

        booking.save(update_fields=["booking_status", "payment_status"])

        return Response({"message": "Booking cancelled successfully."})


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_id = request.data.get("event_id")

        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response(
                {"error": "Quantity must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                event = Event.objects.select_for_update().get(event_id=event_id)

                if event.available_seats < quantity:
                    return Response(
                        {"error": f"Only {event.available_seats} seats are available."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                total_amount = Decimal(event.fee) * quantity

                razorpay_order = client.order.create({
                    "amount": int(total_amount * 100),
                    "currency": "INR",
                    "payment_capture": 1
                })

                booking = Booking.objects.create(
                    user=request.user,
                    event=event,
                    full_name=request.user.name,
                    email=request.user.email,
                    phone_number=request.user.phone_number,
                    quantity=quantity,
                    ticket_price=event.fee,
                    total_amount=total_amount,
                    razorpay_order_id=razorpay_order["id"],
                    payment_status="pending",
                    booking_status="pending"
                )

                return Response({
                    "booking_id": booking.id,
                    "order_id": razorpay_order["id"],
                    "amount": razorpay_order["amount"],
                    "currency": razorpay_order["currency"],
                    "key": settings.RAZORPAY_KEY_ID
                })

        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get("booking_id")

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        params = {
            "razorpay_order_id": request.data.get("razorpay_order_id"),
            "razorpay_payment_id": request.data.get("razorpay_payment_id"),
            "razorpay_signature": request.data.get("razorpay_signature")
        }

        try:
            client.utility.verify_payment_signature(params)

            booking.razorpay_payment_id = params["razorpay_payment_id"]
            booking.razorpay_signature = params["razorpay_signature"]
            booking.payment_status = "paid"
            booking.booking_status = "confirmed"
            booking.save()

            return Response({
                "message": "Payment Successful",
                "booking_id": booking.id
            })


        except SignatureVerificationError:

            booking.payment_status = "failed"

            booking.booking_status = "cancelled"

            booking.save(update_fields=["payment_status", "booking_status"])

            return Response(

                {"error": "Payment verification failed."},

                status=status.HTTP_400_BAD_REQUEST

            )