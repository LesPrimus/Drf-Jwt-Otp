import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_otp.models import Device


def get_code_token_max_age():
    return getattr(settings, 'CODE_TOKEN_MAX_AGE', 60 * 5)


class BaseAbstractToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4)
    device_persistent_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def generate_token(cls, device: Device):
        code_token, _ = cls.objects.update_or_create(
            user=device.user,
            device_persistent_id=device.persistent_id,
            defaults={
                'valid_until': timezone.now() + timezone.timedelta(seconds=get_code_token_max_age()),
                'uuid': uuid.uuid4()
            }
        )
        return code_token.uuid

    @classmethod
    def get_instance_from_uuid(cls, code_token):
        try:
            device_token = cls.objects.get(uuid=code_token)
        except cls.DoesNotExist:
            pass
        else:
            if device_token.is_valid():
                return device_token
        return None

    @classmethod
    def delete_user_instances(cls, user_id):
        deleted = cls.objects.filter(user_id=user_id).delete()
        return deleted

    def is_valid(self):
        return self.valid_until > timezone.now()


class OtpDeviceToken(BaseAbstractToken):
    class Meta(BaseAbstractToken.Meta):
        unique_together = ['user', 'device_persistent_id']


class RememberDeviceToken(BaseAbstractToken):
    def is_valid(self, user=None):
        device = Device.from_persistent_id(self.device_persistent_id)
        if not device:
            return False
        else:
            user = user or device.user
            if not user == self.user:
                return False
        return super(RememberDeviceToken, self).is_valid()
