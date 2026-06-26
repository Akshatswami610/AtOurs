from django.db import models
from django.conf import settings
from datetime import time

User = settings.AUTH_USER_MODEL

class PartyCategory(models.TextChoices):
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

class Party(models.Model):
    party_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    party_name = models.CharField(max_length=100)
    party_category = models.CharField(max_length=100, choices=PartyCategory.choices, db_index=True)
    description = models.TextField()
    max_members = models.PositiveIntegerField()
    fee = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.ANY)
    age_limit = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    party_date = models.DateField(db_index=True)
    party_time = models.TimeField(default=time(22, 0))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["party_date", "party_time"]

    def __str__(self):
        return self.party_name


class PartyPoster(models.Model):
    poster_id = models.AutoField(primary_key=True)
    party = models.ForeignKey( Party, on_delete=models.CASCADE, related_name="posters")
    poster = models.ImageField(upload_to="party_posters/")

    def __str__(self):
        return f"{self.party.party_name} Poster"