# flake8: noqa
import os
import random
import string
from datetime import datetime, timedelta

import jwt
from rest_framework import generics, permissions, views
from rest_framework.exceptions import *
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    smart_bytes,
    smart_str,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from templates.emails.mailer import (
    send_password_reset_email,
    send_register_owner_by_shop_email,
    send_request_create_owner_email,
    send_verify_code_email,
)
from .models import RequestOwner, RequestOwnerStatus
from utilities import email_helper

from .models import User, UserStatusType, UserVerifyCode
from .renderers import UserRenderer
from .serializers import (
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    GetUserSerializer,
    LoginSerializer,
    LoginVerifySerializer,
    LogoutSerializer,
    RegisterSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    ShopRegisterSerializer,
    UserVerifySerializer,
)


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get("APP_SCHEME"), "http", "https"]


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        request_data["status"] = RequestOwnerStatus.WAITING_FOR_APPROVE
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = RequestOwner.objects.filter(email=user_data["email"]).first()
        user_data["id"] = user.pk
        send_request_create_owner_email(user)

        return Response(user_data, status=status.HTTP_201_CREATED)


class RegisterByShopView(generics.GenericAPIView):
    serializer_class = ShopRegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        gen_password = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )

        print("gen_password:", gen_password)

        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        owner = User.objects.get(email=user_data["email"])
        # send_register_owner_by_shop_email(owner, gen_password)
        owner.password = make_password(gen_password)
        owner.is_first_login = True
        owner.is_verified = True
        owner.status = UserStatusType.INACTIVE
        owner.save()
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=settings.SIMPLE_JWT["ALGORITHM"]
            )
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response(
                {"email": "Successfully activated"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError as identifier:
            print("Activation Expired")
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            print("identifier", identifier)

            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(views.APIView):
    serializer_class = LoginSerializer
    serializer_user_verify_code_class = UserVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data["email"])
        gen_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        exp_in = timezone.now() + timedelta(minutes=3)

        user_verify_code = {"user": user.id, "code": gen_code, "expire_time": exp_in}

        serializer_user_verify_code = self.serializer_user_verify_code_class(
            data=user_verify_code, many=False
        )
        serializer_user_verify_code.is_valid(raise_exception=True)
        serializer_user_verify_code.save()

        gen_code = serializer_user_verify_code.data["code"]

        print("gen_code:", gen_code)

        # send_verify_code_email(user, gen_code)

        return Response(
            {
                "is_send_code": True,
                "message": "Send code verify for mail success",
                "email": request.data["email"],
                "uidb64": urlsafe_base64_encode(smart_bytes(user.id)),
            },
            status=status.HTTP_200_OK,
        )


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        if User.objects.filter(email=email).first() is None:
            raise ValidationError("email not exist.")

        if User.objects.filter(email=email, status=UserStatusType.ACTIVE).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                "password-reset-confirm",
                kwargs={"uidb64": uidb64, "token": token, "version": "v1"},
            )

            redirect_url = request.data.get("redirect_url", "")
            send_password_reset_email(user, current_site, relativeLink, redirect_url)
        return Response(
            {"success": "We have sent you a link to reset your password"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token, *args, **kwargs):
        redirect_url = request.GET.get("redirect_url")
        try:
            id_auto_gen = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id_auto_gen)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + "?token_valid=False")
                else:
                    return CustomRedirect(
                        os.environ.get("FRONTEND_URL", "") + "?token_valid=False"
                    )

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url
                    + "?token_valid=True&message=Credentials Valid&uidb64="
                    + uidb64
                    + "&token="
                    + token
                )
            else:
                return CustomRedirect(
                    os.environ.get("FRONTEND_URL", "") + "?token_valid=False"
                )

        except DjangoUnicodeDecodeError as identifier:
            print(str(identifier))
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + "?token_valid=False")

            except UnboundLocalError as err:
                print(err)
                return Response(
                    {"error": "Token is not valid, please request a new one"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset success"},
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class GetUserFromAccessTokenAPIView(views.APIView):
    serializer_class = GetUserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token_obj = AccessToken(
            request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer ", "")
        )
        user_id = access_token_obj["user_id"]
        user = User.objects.get(id=user_id)
        uidb64 = (urlsafe_base64_encode(smart_bytes(user_id)),)
        return JsonResponse(
            {
                "user_id": user.id,
                "uidb64": uidb64,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_first_login": user.is_first_login,
                "role_id": 5,
                "role_name": "OWNER",
            },
            status=status.HTTP_200_OK,
        )


# Password Change API
class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "Password updated successfully",
            "data": [],
        }
        return Response(response)


# Login verify code
class LoginVerifyAPIView(views.APIView):
    serializer_class = LoginVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# resend code verify
class ResendCodeVerifyAPIView(views.APIView):
    serializer_user_verify_code_class = UserVerifySerializer

    def post(self, request, *args, **kwargs):
        if "email" not in request.data:
            raise ValidationError("Please enter email.")
        try:
            user = User.objects.get(email=request.data["email"])
        except User.DoesNotExist:
            raise NotFound(
                "This user doesn't seem to exist."
            )
        gen_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        exp_in = timezone.now() + timedelta(minutes=3)
        user_verify_code = {"user": user.id, "code": gen_code, "expire_time": exp_in}
        serializer_user_verify_code = self.serializer_user_verify_code_class(
            data=user_verify_code, many=False
        )
        serializer_user_verify_code.is_valid(raise_exception=True)
        serializer_user_verify_code.save()

        gen_code = serializer_user_verify_code.data["code"]
        send_verify_code_email(user, gen_code)

        return Response(
            {
                "is_send_code": True,
                "message": "Send code verify for mail success",
                "email": request.data["email"],
                "uidb64": urlsafe_base64_encode(smart_bytes(user.id)),
            },
            status=status.HTTP_200_OK,
        )
