from collections import defaultdict

from django_otp import devices_for_user

from drf_jwt_otp.models import OtpDeviceToken


class JwtCreateResponseOtpPayload:

    @classmethod
    def user_otp_enabled(cls, user):
        return any([
            d for d in devices_for_user(user=user, confirmed=True)
        ])

    @classmethod
    def get_user_otp_payload(cls, user):
        devices = defaultdict(list)
        for device in devices_for_user(user, confirmed=True):
            device_kls = device.__class__
            devices[device_kls.__name__].append(
                {'name': device.name, 'code_token': OtpDeviceToken.generate_token(device)}
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
