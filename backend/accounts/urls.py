from django.urls import path
from .views import RegisterView, LoginView, LogoutView, MeView, ForgotPasswordView, VerifyOTPView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path( "forgot-password/", ForgotPasswordView.as_view(), name="forgot-password" ),
    path( "verify-otp/", VerifyOTPView.as_view(), name="verify-otp" ),
    path( "reset-password/", ResetPasswordView.as_view(), name="reset-password" ),
]