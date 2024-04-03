import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django_extensions.db.models import TimeStampedModel

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        first_name,
        last_name,
        email,
        is_first_login,
        is_verified,
        password=None,
        status=None,
    ):
        if username is None:
            raise TypeError("Users should have a username")
        if email is None:
            raise TypeError("Users should have a Email")

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
            is_first_login=is_first_login,
            is_verified=is_verified,
            status=status,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        username,
        email,
        is_first_login=True,
        is_verified=True,
        password=None,
    ):
        if password is None:
            raise TypeError("Password should not be none")
        user = self.create_user(
            username,
            "",
            "",
            email,
            is_first_login,
            is_verified,
            password,
            UserStatusType.ACTIVE,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class UserStatusType(models.TextChoices):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    APPROVED = "APPROVED"


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=125, blank=True)
    last_name = models.CharField(max_length=125, blank=True)
    phone = models.CharField(max_length=125, blank=True)
    address = models.CharField(max_length=225, blank=True)
    prefecture = models.CharField(max_length=225, blank=True)
    address_detail = models.CharField(max_length=225, blank=True)
    postcode = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_check_notification_at = models.DateTimeField(
        default=timezone.now, db_index=True
    )
    last_change_password_at = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=125,
        choices=UserStatusType.choices,
        default=UserStatusType.INACTIVE,
        blank=True,
    )
    notes = models.TextField(blank=True, null=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # because we not using username then we auto gen username
        username = ""
        if not self.username or self.username == "":
            username = uuid.uuid4().hex[:30]
        else:
            username = self.username
        counter = 1
        while User.objects.filter(username=username):
            username = username + str(counter)
            counter += 1
        self.username = username

        super().save(*args, **kwargs)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        try:
            full_name = f"{self.last_name}{self.first_name}"
        except AttributeError:
            full_name = self.email
        return full_name.strip()

class UserVerifyCode(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=8)
    expire_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    user = models.ForeignKey(
        "User", to_field="id", related_name="user_verify_code", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "user_verify_code"


class RequestOwnerStatus(models.TextChoices):
    WAITING_FOR_APPROVE = "WAITING_FOR_APPROVE"
    REJECT = "REJECT"
    APPROVED = "APPROVED"

class RequestOwner(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=125, blank=True)
    first_name = models.CharField(max_length=125, blank=True)
    last_name = models.CharField(max_length=125, blank=True)
    phone = models.CharField(max_length=125, blank=True)
    address = models.CharField(max_length=225, null=True, blank=True, default="")
    prefecture = models.CharField(max_length=225, null=True, blank=True, default="")
    postcode = models.CharField(max_length=50, null=True, blank=True, default="")
    address_detail = models.CharField(max_length=225, null=True, blank=True, default="")
    status = models.CharField(
        max_length=125,
        choices=RequestOwnerStatus.choices,
        default=RequestOwnerStatus.WAITING_FOR_APPROVE,
        blank=True,
    )
    notes = models.TextField(blank=True, null=True, default="")

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        try:
            full_name = f"{self.last_name}{self.first_name}"
        except AttributeError:
            full_name = self.email
        return full_name.strip()
