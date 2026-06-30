from django.urls import path
from .views import EventListCreateView, EventDetailView

urlpatterns = [
    path("events/", EventListCreateView.as_view(), name="event-list"),
    path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
]