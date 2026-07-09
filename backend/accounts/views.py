import random

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import PasswordResetOTP  # adjust import path to match your app
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()


# -----------------------------
# USER PROFILE
# -----------------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "date_of_birth": user.date_of_birth,
        })

    def patch(self, request):
        user = request.user

        # Email changes go through a check for uniqueness/format instead of
        # being written straight from the request, since this bypasses the
        # serializer validation RegisterView/LoginView rely on.
        new_email = request.data.get("email")
        if new_email and new_email.lower() != user.email.lower():
            if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                return Response(
                    {"error": "That email is already in use."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = new_email

        user.name = request.data.get("name", user.name)
        user.phone_number = request.data.get(
            "phone_number",
            user.phone_number,
        )

        if "date_of_birth" in request.data:
            user.date_of_birth = request.data["date_of_birth"]

        user.save()

        return Response({
            "message": "Profile updated successfully."
        })

    def delete(self, request):
        user = request.user
        password = request.data.get("password")

        if not password:
            return Response(
                {"error": "Password is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify password
        if not user.check_password(password):
            return Response(
                {"error": "Incorrect password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()

        # 204 responses must not carry a body per the HTTP spec, so return
        # 200 here if the frontend needs the confirmation message.
        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_200_OK
        )


# -----------------------------
# REGISTER
# -----------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# -----------------------------
# LOGIN
# -----------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # NOTE: returning a distinct "account not found" vs "wrong password"
        # response is intentional for UX, but it does allow email
        # enumeration. If that's a concern for this product, collapse both
        # branches below into one generic "Invalid email or password."
        if not User.objects.filter(email__iexact=email).exists():
            return Response(
                {
                    "error": "No account found with this email.",
                    "code": "account_not_found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user is None:
            return Response(
                {
                    "error": "Incorrect password.",
                    "code": "invalid_password",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "date_of_birth": user.date_of_birth,
            },
            "message": "Login successful.",
        })


# -----------------------------
# LOGOUT
# -----------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Filter+delete instead of request.user.auth_token.delete() so this
        # doesn't raise Token.DoesNotExist if the token was already removed.
        Token.objects.filter(user=request.user).delete()

        return Response({
            "message": "Logged out successfully."
        })


# -----------------------------
# PASSWORD RESET FLOW
# -----------------------------
class OTPThrottle(AnonRateThrottle):
    rate = "5/min"


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Remove previous OTPs so only one is ever valid at a time
        PasswordResetOTP.objects.filter(user=user).delete()

        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp,
        )

        send_mail(
            subject="Password Reset OTP",
            message=f"""Hello {user.name},

Your OTP is:

{otp}

It is valid for 5 minutes.

If you didn't request this, ignore this email.

House Party Marketplace
""",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"message": "OTP sent successfully."}
        )


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            otp_obj = PasswordResetOTP.objects.get(
                user=user,
                otp=otp,
            )
        except PasswordResetOTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_obj.expires_at:
            otp_obj.delete()
            return Response(
                {"error": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True
        otp_obj.save()

        return Response(
            {"message": "OTP verified successfully."}
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            otp_obj = PasswordResetOTP.objects.get(
                user=user,
                otp=otp,
                is_verified=True,
            )
        except PasswordResetOTP.DoesNotExist:
            return Response(
                {"error": "OTP not verified."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_obj.expires_at:
            otp_obj.delete()
            return Response(
                {"error": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.save()

        # Clean up all OTPs for this user, not just the one used, so no
        # stray verified/unverified OTPs are left valid afterward.
        PasswordResetOTP.objects.filter(user=user).delete()

        return Response(
            {"message": "Password reset successfully."}
        )
