from django.contrib import admin

# Register your models here.
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "last_check_notification_at",
        "created_at",
    ]

    def save_model(self, request, obj, form, change) -> None:
        if obj.password is None:
            obj.password = ""
        return super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
