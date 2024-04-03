from django.db import models
from django.utils import timezone


class Area(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "area"
        app_label = 'status'
        ordering = ["-id"]

class Status(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "status"
        app_label = 'status'
        ordering = ["-id"]
