import uuid
from collections import defaultdict

from django.utils import timezone
from django_otp import devices_for_user
from django_otp.models import Device

from drf_jwt_otp.models import OtpDeviceToken, get_code_token_max_age


class JwtCreateResponseOtpPayload:

    @classmethod
    def user_otp_enabled(cls, user):
        return any([
            d for d in devices_for_user(user=user, confirmed=True)
        ])

    @classmethod
    def generate_device_code_token(cls, device: Device):
        code_token, _ = OtpDeviceToken.objects.update_or_create(
            user=device.user,
            device_persistent_id=device.persistent_id,
            defaults={
                'valid_until': timezone.now() + timezone.timedelta(seconds=get_code_token_max_age()),
                'uuid': uuid.uuid4()
            }
        )
        return code_token.uuid

    @classmethod
    def get_user_otp_payload(cls, user):
        devices = defaultdict(list)
        for device in devices_for_user(user, confirmed=True):
            devices[device.__class__.__name__].append(
                {'name': device.name, 'code_token': cls.generate_device_code_token(device)}
            )
        return devices

    @classmethod
    def jwt_create_response_payload(cls, token, user=None, request=None, issued_at=None):
        return {'pk': issued_at, 'token': token}

    def __call__(self, token, user=None, request=None, issued_at=None):
        if user and self.user_otp_enabled(user):
            return self.get_user_otp_payload(user)
        return self.jwt_create_response_payload(token, user, request, issued_at)


jwt_create_response_otp_payload = JwtCreateResponseOtpPayload()
