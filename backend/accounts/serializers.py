from datetime import date

from rest_framework import serializers

from .models import User, UserProfile, Interest


# ==========================================================
# REGISTER - SEND OTP
# ==========================================================

class RegisterSendOTPSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    date_of_birth = serializers.DateField()

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate_phone_number(self, value):
        value = value.strip()

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
            (today.month, today.day) <
            (value.month, value.day)
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

    profile_image = serializers.ImageField(
        required=True
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    otp = serializers.CharField(
        max_length=6,
        min_length=6
    )

    def validate_email(self, value):
        return value.lower().strip()

    def validate_phone_number(self, value):
        return value.strip()


# ==========================================================
# PASSWORD LOGIN
# ==========================================================

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

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

    otp = serializers.CharField(
        max_length=6,
        min_length=6
    )

    def validate_email(self, value):
        return value.lower().strip()


# ==========================================================
# FORGOT PASSWORD
# ==========================================================

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower().strip()

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email."
            )

        return value


# ==========================================================
# VERIFY RESET OTP
# ==========================================================

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6,
        min_length=6
    )

    def validate_email(self, value):
        return value.lower().strip()


# ==========================================================
# RESET PASSWORD
# ==========================================================

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6,
        min_length=6
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate_email(self, value):
        return value.lower().strip()

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
    current_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs


# ==========================================================
# INTEREST
# ==========================================================

class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = [
            "id",
            "name",
        ]


# ==========================================================
# USER PROFILE
# ==========================================================

class UserProfileSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(
        many=True,
        read_only=True
    )

    interest_ids = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="interests",
    )

    class Meta:
        model = UserProfile

        fields = [
            "profile_image",
            "bio",
            "interests",
            "interest_ids",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
        ]


# ==========================================================
# CURRENT USER
# ==========================================================

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(
        read_only=True
    )

    class Meta:
        model = User

        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "date_of_birth",
            "profile",
            "date_joined",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "email",
            "date_joined",
            "updated_at",
        ]