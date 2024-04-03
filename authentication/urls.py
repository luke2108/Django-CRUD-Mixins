from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path
from django.views.generic import RedirectView

from .views import (
    ChangePasswordView,
    GetUserFromAccessTokenAPIView,
    LoginAPIView,
    LoginVerifyAPIView,
    LogoutAPIView,
    PasswordTokenCheckAPI,
    RegisterByShopView,
    RegisterView,
    RequestPasswordResetEmail,
    ResendCodeVerifyAPIView,
    SetNewPasswordAPIView,
    VerifyEmail,
)

urlpatterns = [
    path("", RedirectView.as_view(url="login/", permanent=False)),
    path("register/", RegisterView.as_view(), name="register"),
    path("register", RegisterByShopView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("login/verify_code/", LoginVerifyAPIView.as_view(), name="login_verify_code"),
    path("login/resend_code/", ResendCodeVerifyAPIView.as_view(), name="resend_code"),
    path("me/", GetUserFromAccessTokenAPIView.as_view(), name="get-user"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("email-verify/", VerifyEmail.as_view(), name="email-verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "request-reset-password/",
        RequestPasswordResetEmail.as_view(),
        name="request-reset-password",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete/",
        SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path("password-change/", ChangePasswordView.as_view(), name="password-change"),
]
