from rest_framework import serializers
from .models import Event, SavedEvent
from accounts.models import User
from django.utils import timezone

class EventHostSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "profile_image",
        ]

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile and obj.profile.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profile_image.url)
            return obj.profile.profile_image.url
        return None


class EventSerializer(serializers.ModelSerializer):
    user = EventHostSerializer(read_only=True)
    host_events = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField()
    booked_seats = serializers.ReadOnlyField()
    available_seats = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()

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
            "event_end_time",
            "status",
            "booked_seats",
            "available_seats",
            "is_sold_out",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "event_id",
            "user",
            "host_events",
            "status",
            "booked_seats",
            "available_seats",
            "is_sold_out",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        event_date = attrs.get("event_date", getattr(self.instance, "event_date", None))
        event_time = attrs.get("event_time", getattr(self.instance, "event_time", None))
        event_end_time = attrs.get("event_end_time", getattr(self.instance, "event_end_time", None))

        today = timezone.localdate()
        current_time = timezone.localtime().time()

        # Event date cannot be in the past
        if event_date and event_date < today:
            raise serializers.ValidationError({
                "event_date": "Event date cannot be in the past."
            })

        # If event is today, time must be in the future
        if event_date == today and event_time and event_time <= current_time:
            raise serializers.ValidationError({
                "event_time": "Event time must be in the future."
            })

        if event_time and event_end_time and event_end_time <= event_time:
            raise serializers.ValidationError({
                "event_end_time": "Event end time must be after event time."
            })

        return attrs

    def get_host_events(self, obj):
        return Event.objects.filter(user=obj.user).count()

class SavedEventSerializer(serializers.ModelSerializer):

    event = EventSerializer(read_only=True)

    class Meta:
        model = SavedEvent
        fields = [
            "id",
            "user",
            "event",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]