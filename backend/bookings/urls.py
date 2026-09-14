from django.urls import path
from .views import  *

urlpatterns = [
    path( "", BookingListCreateView.as_view(), name="booking-list" ),
    path( "<int:pk>/", BookingDetailView.as_view(), name="booking-detail" ),
    path( "create-order/", CreateOrderView.as_view(), name="create-order" ),
    path( "verify-payment/", VerifyPaymentView.as_view(), name="verify-payment" ),
    path( "<int:booking_id>/cancel/", CancelBookingView.as_view(), name="cancel-booking" ),
    path( "event/<int:event_id>/attendees/", EventAttendeesView.as_view(), name="event-attendees" ),
]