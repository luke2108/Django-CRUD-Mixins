import re
from ast import List

from rest_framework import serializers
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    ParseError,
)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from .models import RequestOwner
from .models import User, UserStatusType, UserVerifyCode

class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = RequestOwner
        fields = [
            "email",
            "first_name",
            "last_name",
            "address",
            "prefecture",
            "address_detail",
            "postcode",
            "phone",
            "notes",
            "created",
        ]

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        return email

class UserShopRegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "notes",
            "postcode",
            "address",
            "address_detail",
            "full_name",
            "prefecture",
            "phone",
            "created_at",
        )

class ShopRegisterSerializer(UserShopRegisterSerializer):
    email = serializers.EmailField()


    class Meta:
        model = User
        fields = UserShopRegisterSerializer.Meta.fields
        extra_kwargs = {}

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")

        return email

    def create(self, validated_data):

        user = list(validated_data)
        instance = User(
            **{
                "email": validated_data["email"],
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
                "status": UserStatusType.ACTIVE,
                "notes": validated_data["notes"],
                "postcode": validated_data["postcode"],
                "address": validated_data["address"],
                "address_detail": validated_data["address_detail"],
                "prefecture": validated_data["prefecture"],
                "phone": validated_data["phone"],
            }
        )
        instance.save()

        return instance

    def get_full_name(self, obj):
        return obj.get_full_name()


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "username", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials, try again")
        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        if user.status == UserStatusType.INACTIVE and user.is_first_login is False:
            raise AuthenticationFailed("User is inactive.")

        return super().validate(attrs)


class LoginVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    code = serializers.CharField(max_length=68, min_length=4, write_only=True)

    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "tokens", "uidb64", "code"]

    def get_tokens(self, obj):
        user = User.objects.get(email=obj["email"])

        return {"refresh": user.tokens()["refresh"], "access": user.tokens()["access"]}

    def validate(self, attrs):
        try:
            code = attrs.get("code")
            uidb64 = attrs.get("uidb64")
            id_auto_gen = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id_auto_gen)
            user_verify_code = UserVerifyCode.objects.get(user_id=id_auto_gen)
            if not user_verify_code:
                raise NotFound("Not fount veify code, try again")
            if not (
                user_verify_code.code == code
                and user_verify_code.expire_time > timezone.now()
            ):
                raise ParseError("user_verify_code fail or expired time")

        except Exception as err:
            print(err)
            raise ParseError("Code verify is invalid")

        UserVerifyCode.objects.filter(user_id=id_auto_gen).delete()
        return {"email": user.email, "username": user.username, "tokens": user.tokens}


class UserVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerifyCode
        fields = ["code", "user", "expire_time"]

    def create(self, validated_data):
        UserVerifyCode.objects.filter(user_id=int(validated_data["user"].id)).delete()
        user_verify_user = UserVerifyCode.objects.create(**validated_data)

        return user_verify_user


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id_auto_gen = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id_auto_gen)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)
            reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*(\d+))(?=.*[@$!%*#?&])[A-Za-z(\d+)@$!#%*?&]{8,32}$"
            # compiling regex
            pat = re.compile(reg)
            # searching regex
            mat = re.search(pat, password)
            if not mat:
                raise serializers.ValidationError(_("password is invalid"))

            user.set_password(password)
            user.last_change_password_at = timezone.now()
            user.save()

            return user
        except Exception as err:
            print(err)
            raise AuthenticationFailed("The reset link is invalid", 401)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {"message": (_("Token is expired or invalid"))}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            pass
            # self.fail("bad_token")


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password_confirm = serializers.CharField(
        max_length=128, write_only=True, required=True
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Your old password was entered incorrectly. Please enter it again.")
            )
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": _("The two password fields didn't match.")}
            )

        password = data["new_password"]
        reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*(\d+))(?=.*[@$!%*#?&])[A-Za-z(\d+)@$!#%*?&]{8,32}$"
        # compiling regex
        pat = re.compile(reg)
        # searching regex
        mat = re.search(pat, password)
        if not mat:
            raise serializers.ValidationError(_("password is invalid"))
        return data

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        if user.is_first_login is True:
            user.is_first_login = False
            user.status = UserStatusType.ACTIVE
        user.last_change_password_at = timezone.now()
        user.save()
        return user
