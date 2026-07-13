import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from .models import OTPVerification
from .serializers import  *
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


User = get_user_model()

# --------------------------------------------------
# OTP THROTTLE
# --------------------------------------------------

class OTPThrottle(AnonRateThrottle):
    rate = "5/min"


# --------------------------------------------------
# OTP HELPER
# --------------------------------------------------

def send_otp_email(email, otp, purpose):
    subject = f"AtOurs Marketplace - {purpose}"

    # Plain text fallback
    text_content = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 5 minutes.

If you didn't request this, please ignore this email.

AtOurs Marketplace
"""

    # Render HTML template
    html_content = render_to_string(
        "otp-mail.html",
        {
            "otp": otp,
            "purpose": purpose,
        },
    )

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )

    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


# --------------------------------------------------
# PROFILE
# --------------------------------------------------

class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "date_of_birth": user.date_of_birth
        })

    def patch(self, request):
        user = request.user
        user.name = request.data.get( "name", user.name )
        user.phone_number = request.data.get( "phone_number", user.phone_number)

        user.save()

        return Response({
            "message": "Profile updated successfully."
        })

    def delete(self, request):
        user = request.user

        # Delete auth token
        Token.objects.filter(user=user).delete()

        # Delete user
        user.delete()

        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# --------------------------------------------------
# REGISTER - SEND OTP
# --------------------------------------------------

class RegisterSendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = RegisterSendOTPSerializer( data=request.data )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        OTPVerification.objects.filter(
            email=data["email"],
            otp_type="register"
        ).delete()

        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            email=data["email"],
            otp=otp,
            otp_type="register"
        )

        send_otp_email( data["email"], otp, "Registration OTP")
        return Response({
            "message": "OTP sent successfully."
        })


# --------------------------------------------------
# REGISTER - VERIFY OTP
# --------------------------------------------------

class RegisterVerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = RegisterVerifyOTPSerializer( data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            otp_obj = OTPVerification.objects.get(
                email=data["email"],
                otp=data["otp"],
                otp_type="register"
            )

        except OTPVerification.DoesNotExist:

            return Response(
                {
                    "error": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_obj.expires_at:
            otp_obj.delete()
            return Response(
                {
                    "error": "OTP expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=data["email"],
            phone_number=data["phone_number"],
            name=data["name"],
            date_of_birth=data["date_of_birth"],
            password=data["password"]
        )

        otp_obj.delete()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number
            },
            "message": "Registration successful."
        })


# --------------------------------------------------
# LOGIN WITH PASSWORD
# --------------------------------------------------

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(
            request,
            email=email,
            password=password
        )
        if user is None:
            return Response(
                {
                    "error": "Invalid email or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "date_of_birth": user.date_of_birth
            },
            "message": "Login successful."
        })


# --------------------------------------------------
# LOGIN SEND OTP
# --------------------------------------------------

class LoginSendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = LoginSendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        OTPVerification.objects.filter(email=email,otp_type="login").delete()
        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            email=email,
            otp=otp,
            otp_type="login"
        )
        send_otp_email(
            email,
            otp,
            "Login OTP"
        )

        return Response({
            "message": "OTP sent successfully."
        })


# --------------------------------------------------
# LOGIN VERIFY OTP
# --------------------------------------------------

class LoginVerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):

        serializer = LoginVerifyOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                otp=otp,
                otp_type="login"
            )

        except OTPVerification.DoesNotExist:
            return Response(
                {
                    "error": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_obj.expires_at:
            otp_obj.delete()
            return Response(
                {
                    "error": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response(
                {
                    "error": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        otp_obj.delete()

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "date_of_birth": user.date_of_birth
            },
            "message": "Login successful."
        })


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()

        return Response({
            "message": "Logged out successfully."
        })


# --------------------------------------------------
# FORGOT PASSWORD - SEND OTP
# --------------------------------------------------

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            User.objects.get(email=email)

        except User.DoesNotExist:
            return Response(
                {
                    "error": "No account found with this email."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        OTPVerification.objects.filter(
            email=email,
            otp_type="reset_password"
        ).delete()

        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            email=email,
            otp=otp,
            otp_type="reset_password"
        )
        send_otp_email(
            email,
            otp,
            "Password Reset OTP"
        )

        return Response({
            "message": "OTP sent successfully."
        })


# --------------------------------------------------
# VERIFY RESET OTP
# --------------------------------------------------

class VerifyOTPView(APIView):

    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                otp=otp,
                otp_type="reset_password"
            )

        except OTPVerification.DoesNotExist:
            return Response(
                {
                    "error": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_obj.expires_at:
            otp_obj.delete()
            return Response(
                {
                    "error": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True
        otp_obj.save()
        return Response({
            "message": "OTP verified successfully."
        })


# --------------------------------------------------
# RESET PASSWORD
# --------------------------------------------------

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.objects.get(email=data["email"])

        except User.DoesNotExist:
            return Response(
                {
                    "error": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            otp_obj = OTPVerification.objects.get(
                email=data["email"],
                otp=data["otp"],
                otp_type="reset_password",
                is_verified=True
            )

        except OTPVerification.DoesNotExist:
            return Response(
                {
                    "error": "OTP not verified."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_obj.expires_at:
            otp_obj.delete()
            return Response(
                {
                    "error": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(data["password"])
        user.save()
        OTPVerification.objects.filter(
            email=data["email"],
            otp_type="reset_password"
        ).delete()

        return Response({
            "message": "Password reset successfully."
        })

# --------------------------------------------------
# CHANGE PASSWORD
# --------------------------------------------------

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]
        if not user.check_password(current_password):
            return Response(
                {
                    "error": "Current password is incorrect."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if current_password == new_password:
            return Response(
                {
                    "error": "New password must be different from the current password."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {
                "message": "Password changed successfully."
            }
        )