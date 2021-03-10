from collections import defaultdict

from django_otp import devices_for_user

from drf_jwt_otp.models import OtpDeviceToken, RememberDeviceToken


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

    @classmethod
    def has_remember_cookie(cls, request, user):
        from django.conf import settings
        if cls.validate_otp_cookie(request.COOKIES, user, settings.REMEMBER_COOKIE_NAME):
            return True
        return False

    @classmethod
    def validate_otp_cookie(cls, cookies, user, cookie_name):
        try:
            cookie_value = cookies[cookie_name]
        except KeyError:
            return False
        else:
            try:
                token = RememberDeviceToken.objects.get(uuid=cookie_value)
            except RememberDeviceToken.DoesNotExist:
                return False
            else:
                return token.is_valid(user)

    def __call__(self, token, user=None, request=None, issued_at=None):
        if user and self.user_otp_enabled(user):
            if request and self.has_remember_cookie(request, user):
                pass
            else:
                return self.get_user_otp_payload(user)
        return self.jwt_create_response_payload(token, user, request, issued_at)


jwt_create_response_otp_payload = JwtCreateResponseOtpPayload()
