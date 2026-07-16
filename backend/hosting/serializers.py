from rest_framework import serializers
from .models import Event
from accounts.models import User
from django.utils import timezone

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
            "rules",
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

    def validate(self, attrs):
        event_date = attrs.get("event_date")
        event_time = attrs.get("event_time")

        today = timezone.localdate()
        current_time = timezone.localtime().time()

        # Event date cannot be in the past
        if event_date < today:
            raise serializers.ValidationError({
                "event_date": "Event date cannot be in the past."
            })

        # If event is today, time must be in the future
        if event_date == today and event_time <= current_time:
            raise serializers.ValidationError({
                "event_time": "Event time must be in the future."
            })

        return attrs

    def get_host_events(self, obj):
        return Event.objects.filter(user=obj.user).count()