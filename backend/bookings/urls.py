from django.urls import path
from .views import BookingListCreateView, BookingDetailView, EventAttendeesView

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list"),
    path("<int:pk>/", BookingDetailView.as_view(),name="booking-detail"),
    path("event/<int:event_id>/attendees/", EventAttendeesView.as_view(), name="event-attendees"),

]