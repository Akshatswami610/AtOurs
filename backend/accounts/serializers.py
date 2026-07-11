from datetime import date

from rest_framework import serializers
from .models import User


# ==========================================================
# REGISTER - SEND OTP
# ==========================================================

class RegisterSendOTPSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    date_of_birth = serializers.DateField()
    password = serializers.CharField( write_only=True, min_length=8)
    confirm_password = serializers.CharField( write_only=True )

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )
        return value

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits."
            )

        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "Phone number already exists."
            )

        return value

    def validate_date_of_birth(self, value):
        today = date.today()
        age = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )

        if age < 18:
            raise serializers.ValidationError(
                "You must be at least 18 years old."
            )
        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs


# ==========================================================
# REGISTER - VERIFY OTP
# ==========================================================

class RegisterVerifyOTPSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    date_of_birth = serializers.DateField()
    password = serializers.CharField(write_only=True)
    otp = serializers.CharField(max_length=6)


# ==========================================================
# PASSWORD LOGIN
# ==========================================================

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField( write_only=True )

    def validate_email(self, value):
        return value.lower().strip()


# ==========================================================
# LOGIN OTP - SEND
# ==========================================================

class LoginSendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):

        value = value.lower().strip()

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email."
            )

        return value


# ==========================================================
# LOGIN OTP - VERIFY
# ==========================================================

class LoginVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


# ==========================================================
# FORGOT PASSWORD
# ==========================================================

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


# ==========================================================
# VERIFY RESET OTP
# ==========================================================

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


# ==========================================================
# RESET PASSWORD
# ==========================================================

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField( write_only=True)
    new_password = serializers.CharField( write_only=True, min_length=8)
    confirm_password = serializers.CharField( write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password":
                    "Passwords do not match."
            })
        return attrs