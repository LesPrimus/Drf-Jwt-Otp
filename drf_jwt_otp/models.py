import uuid

from django.conf import settings
from django.db import models


def get_code_token_max_age():
    return getattr(settings, 'CODE_TOKEN_MAX_AGE', 60 * 5)


class BaseAbstractToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4)
    device_persistent_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'device_persistent_id']
        abstract = True


class OtpDeviceToken(BaseAbstractToken):
    pass
