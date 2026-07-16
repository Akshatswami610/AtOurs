from django.db import models
from django.conf import settings
from datetime import time
from django.db.models import Sum

User = settings.AUTH_USER_MODEL

class EventCategory(models.TextChoices):
    HOUSE_PARTY = "HOUSE_PARTY", "House Party"
    DINNER_PARTY = "DINNER_PARTY", "Dinner Party"
    GAME_NIGHT = "GAME_NIGHT", "Game Night"
    LIVE_MUSIC = "LIVE_MUSIC", "Live Music"
    KARAOKE = "KARAOKE", "Karaoke"
    NETWORKING = "NETWORKING", "Networking"
    BOOK_CLUB = "BOOK_CLUB", "Book Club"
    MOVIE_NIGHT = "MOVIE_NIGHT", "Movie Night"
    COOKING_CLASS = "COOKING_CLASS", "Cooking Class"
    WELLNESS = "WELLNESS", "Wellness"
    ART_CRAFT = "ART_CRAFT", "Art & Craft"
    COFFEE_MEETUP = "COFFEE_MEETUP", "Coffee Meetup"
    CELEBRATION = "CELEBRATION", "Celebration"
    DANCE_PARTY = "DANCE_PARTY", "Dance Party"
    WATCH_PARTY = "WATCH_PARTY", "Watch Party"
    CULTURAL_MEETUP = "CULTURAL_MEETUP", "Cultural Meetup"
    WORKSHOP = "WORKSHOP", "Workshop"
    OPEN_MIC = "OPEN_MIC", "Open Mic"
    OTHER = "OTHER", "Other"


class Gender(models.TextChoices):
    ANY = "ANY", "Any"
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    event_name = models.CharField(max_length=100)
    event_category = models.CharField( max_length=100, choices=EventCategory.choices, db_index=True )
    description = models.TextField()
    rules = models.TextField()
    poster = models.ImageField(upload_to="event_posters/")
    max_members = models.PositiveIntegerField()
    fee = models.PositiveIntegerField(default=0)
    gender = models.CharField( max_length=10, choices=Gender.choices, default=Gender.ANY )
    age_limit = models.PositiveIntegerField()
    location = models.CharField(max_length=255)

    event_date = models.DateField(db_index=True)
    event_time = models.TimeField(default=time(22, 0))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date", "event_time"]

    def __str__(self):
        return self.event_name

    @property
    def booked_seats(self):
        return (
                self.bookings.filter(
                    booking_status__in=["pending", "confirmed"]
                ).aggregate(total=Sum("quantity"))["total"] or 0
        )

    @property
    def available_seats(self):
        return self.max_members - self.booked_seats

    @property
    def is_sold_out(self):
        return self.available_seats <= 0