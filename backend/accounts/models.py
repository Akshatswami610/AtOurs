from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r"^\+?\d{10,15}$",
    message="Enter a valid phone number."
)


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        phone_number,
        name,
        date_of_birth,
        password=None,
        **extra_fields
    ):
        email = self.normalize_email(email)

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

        user = self.model(
            email=email,
            phone_number=phone_number,
            name=name,
            date_of_birth=date_of_birth,
            **extra_fields
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
        **extra_fields
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
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        validators=[phone_validator]
    )

    date_of_birth = models.DateField()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number", "name", "date_of_birth"]

    def __str__(self):
        return f"{self.name} ({self.email})"