from django.contrib import admin
from .models import Event

@admin.register(Event)
class PartyAdmin(admin.ModelAdmin):
    list_display = ["event_name", "user", "event_date","fee",]

    list_filter = ["event_category", "gender"]

    search_fields = ["event_name", "event_category", "gender"]