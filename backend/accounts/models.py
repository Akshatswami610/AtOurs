from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta

import uuid
import os


# =========================================================
# Upload Paths
# =========================================================

def profile_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"profile_images/{uuid.uuid4()}{ext}"


# =========================================================
# Validators
# =========================================================

phone_validator = RegexValidator(
    regex=r"^\+?\d{10,15}$",
    message="Enter a valid phone number.",
)


# =========================================================
# User Manager
# =========================================================

class UserManager(BaseUserManager):

    def create_user(
        self,
        email,
        phone_number,
        name,
        date_of_birth,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Email is required")

        if not phone_number:
            raise ValueError("Phone number is required")

        if not name:
            raise ValueError("Name is required")

        if not date_of_birth:
            raise ValueError("Date of birth is required")

        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            phone_number=phone_number,
            name=name,
            date_of_birth=date_of_birth,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        phone_number,
        name,
        date_of_birth,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            phone_number=phone_number,
            name=name,
            date_of_birth=date_of_birth,
            password=password,
            **extra_fields,
        )


# =========================================================
# User
# =========================================================

class User(AbstractBaseUser, PermissionsMixin):

    name = models.CharField( max_length=150,)
    email = models.EmailField( unique=True, db_index=True,)
    phone_number = models.CharField( max_length=15, unique=True, db_index=True, validators=[phone_validator],)
    date_of_birth = models.DateField()
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True,)
    is_staff = models.BooleanField(default=False,)
    date_joined = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "phone_number",
        "name",
        "date_of_birth",
    ]

    def __str__(self):
        return f"{self.name} ({self.email})"


# =========================================================
# Interests
# =========================================================

class Interest(models.Model):

    name = models.CharField(max_length=50, unique=True,)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


# =========================================================
# User Profile
# =========================================================

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile",)
    profile_image = models.ImageField(upload_to=profile_image_upload_path, blank=True, null=True,)
    bio = models.TextField(max_length=500,blank=True,)
    interests = models.ManyToManyField(Interest, blank=True, related_name="users",)

    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return f"{self.user.name}'s profile"


# =========================================================
# OTP Verification
# =========================================================

OTP_TYPES = [
    ("register", "Register"),
    ("login", "Login"),
    ("reset_password", "Reset Password"),
]


class OTPVerification(models.Model):

    user = models.ForeignKey( User, on_delete=models.CASCADE, null=True, blank=True, related_name="otp_verifications",)
    email = models.EmailField()
    otp = models.CharField(max_length=6,)
    otp_type = models.CharField(max_length=20,choices=OTP_TYPES,)
    is_verified = models.BooleanField(default=False,)

    created_at = models.DateTimeField(auto_now_add=True,)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)

        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.email} - {self.otp_type}"

    class Meta:
        ordering = ["-created_at"]