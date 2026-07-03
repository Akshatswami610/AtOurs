from rest_framework import serializers
from .models import Event
from accounts.models import User


class EventHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
        ]


class EventSerializer(serializers.ModelSerializer):
    user = EventHostSerializer(read_only=True)
    host_events = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "event_id",
            "user",
            "host_events",
            "event_name",
            "event_category",
            "description",
            "poster",
            "max_members",
            "fee",
            "gender",
            "age_limit",
            "location",
            "event_date",
            "event_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "event_id",
            "user",
            "host_events",
            "created_at",
            "updated_at",
        ]

    def get_host_events(self, obj):
        return Event.objects.filter(user=obj.user).count()