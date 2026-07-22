from rest_framework import serializers
from .models import Booking
from hosting.serializers import EventSerializer


class BookingSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"

        read_only_fields = (
            "user",
            "event",
            "payment_status",
            "booking_status",
            "booked_at",
            "updated_at",
            "razorpay_order_id",
            "razorpay_payment_id",
            "razorpay_signature",
        )