from unittest import mock

import pytest
from django_otp.models import Device
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from drf_jwt_otp.models import OtpDeviceToken


def get_otp_device_token_from_device(device):
    try:
        device_token = OtpDeviceToken.objects.get(
            user=device.user,
            device_persistent_id=device.persistent_id
        )
    except OtpDeviceToken.DoesNotExist:
        device_token = None
    return device_token


def check_response_data(response_data, device):
    expected = {device.__class__.__name__: [{
        'code_token': get_otp_device_token_from_device(device).uuid,
        'name': device.name}
    ]}
    assert response_data == expected


@pytest.mark.django_db
class BaseTestView:
    credentials = {'username': 'John', 'password': 'secret'}


class TestJsonWebTokenOtpView(BaseTestView):
    def test_no_otp_user_return_jwt(self, user, call_auth_endpoint):
        res = call_auth_endpoint(self.credentials)
        assert 'token' in res.data

    def test_otp_user_return_custom_payload(self, otp_user, call_auth_endpoint):
        res = call_auth_endpoint(self.credentials)
        check_response_data(res.data, otp_user.device)


class TestVerifyCodeTokenView(BaseTestView):
    def test_valid_code_token_return_jwt(
            self,
            otp_user,
            call_verify_code_token_endpoint,
            monkeypatch
    ):
        code_token_uuid = OtpDeviceToken.generate_token(otp_user.device)
        data = {'code_token': code_token_uuid, 'otp_code': 123456}
        monkeypatch.setattr(otp_user.device.__class__, 'verify_token', lambda _, __: True)
        res = call_verify_code_token_endpoint(data)
        assert 'token' in res.data
