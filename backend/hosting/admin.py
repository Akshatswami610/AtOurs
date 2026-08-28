from django.contrib import admin
from .models import Event, SavedEvent

@admin.register(Event)
class PartyAdmin(admin.ModelAdmin):
    list_display = ["event_name", "user", "event_date","fee",]

    list_filter = ["event_category", "gender"]

    search_fields = ["event_name", "event_category", "gender"]

@admin.register(SavedEvent)
class SavedEventAdmin(admin.ModelAdmin):
    list_display = ["user", "event", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__name", "event__event_name"]