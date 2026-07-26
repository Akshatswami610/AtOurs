from django.urls import path
from .views import *

urlpatterns = [
    path("me/", MeView.as_view()),
    path("users/<int:user_id>/", PublicUserProfileView.as_view()),
    path("interests/", InterestListView.as_view()),

    path("register/send-otp/", RegisterSendOTPView.as_view()),
    path("register/verify/", RegisterVerifyOTPView.as_view()),

    path("login/", LoginView.as_view()),
    path("login/send-otp/", LoginSendOTPView.as_view()),
    path("login/verify/", LoginVerifyOTPView.as_view()),

    path("forgot-password/", ForgotPasswordView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),

    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    path("logout/", LogoutView.as_view()),
]