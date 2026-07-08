from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = ( "id", "user", "event", "quantity", "payment_status", "booking_status", "booked_at",)
    list_filter = ( "payment_status", "booking_status",)
    search_fields = ( "full_name", "email", "phone_number", "razorpay_order_id",)

    ordering = ("-booked_at",)