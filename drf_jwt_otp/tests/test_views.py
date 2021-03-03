import pytest

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
class TestJsonWebTokenOtpView:

    def test_no_otp_user_return_jwt(self, user, call_auth_endpoint):
        data = {'username': 'John', 'password': 'secret'}
        res = call_auth_endpoint(data)
        assert 'token' in res.data

    def test_otp_user_return_custom_payload(self, otp_user, call_auth_endpoint):
        data = {'username': 'John', 'password': 'secret'}
        res = call_auth_endpoint(data)
        check_response_data(res.data, otp_user.device)
