from django.contrib import admin
from .models import Support

@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'timestamp')
    list_filter = ('email', 'phone_number')