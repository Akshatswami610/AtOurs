from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer

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

        user.name = request.data.get("name", user.name)
        user.email = request.data.get("email", user.email)
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

        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
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

        # Checked separately from authenticate() so the frontend can tell
        # "no account with this email" apart from "wrong password" and
        # prompt the person to register instead of just saying "invalid".
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
        request.user.auth_token.delete()

        return Response({
            "message": "Logged out successfully."
        })