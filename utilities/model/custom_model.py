from django.db import models
from django.utils import timezone


class CustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class CustomModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()

    def to_dict(self, include_fields: list = [], exclude_fields: list = []):
        if include_fields and exclude_fields:
            raise Exception(
                "include_fields and exclude_fields not appear at the same time"
            )

        object_dict = self.__dict__
        if include_fields:
            return {
                key: object_dict[key] for key in object_dict if key in include_fields
            }

        if include_fields:
            return {
                key: object_dict[key]
                for key in object_dict
                if key not in exclude_fields
            }

        return object_dict

    objects = CustomManager()
