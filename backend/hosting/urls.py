from django.urls import path
from .views import EventListCreateView, EventDetailView, SaveEventView, RemoveSavedEventView, SavedEventListView

urlpatterns = [
    path("events/", EventListCreateView.as_view(), name="event-list"),
    path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
    path("events/<int:event_id>/save/", SaveEventView.as_view(), name="save-event"),
    path("events/<int:event_id>/unsave/", RemoveSavedEventView.as_view(), name="remove-saved-event"),
    path("saved-events/", SavedEventListView.as_view(), name="saved-events"),
]