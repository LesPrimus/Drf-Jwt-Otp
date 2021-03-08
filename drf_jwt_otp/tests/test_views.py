import uuid

import pytest

from drf_jwt_otp.models import OtpDeviceToken


@pytest.mark.django_db
class BaseTestView:
    credentials = {'username': 'John', 'password': 'secret'}


class TestJsonWebTokenOtpView(BaseTestView):
    def test_no_otp_user_return_jwt(self, user, call_auth_endpoint):
        res = call_auth_endpoint(self.credentials)
        assert res.status_code == 201
        assert 'token' in res.data

    def test_otp_user_return_custom_payload(self, otp_user, call_auth_endpoint):
        res = call_auth_endpoint(self.credentials)
        device_token = OtpDeviceToken.objects.get(
            user_id=otp_user.id,
            device_persistent_id=otp_user.device.persistent_id
        )
        expected = {otp_user.device.__class__.__name__: [{
            'code_token': device_token.uuid,
            'name': otp_user.device.name}
        ]}
        assert res.status_code == 201
        assert res.data == expected


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
        assert res.status_code == 200
        assert 'token' in res.data

    def test_invalid_code_token_return_not_found(
            self,
            otp_user,
            call_verify_code_token_endpoint,
    ):
        code_token_uuid = uuid.uuid4()
        data = {'code_token': code_token_uuid, 'otp_code': 123456}
        res = call_verify_code_token_endpoint(data)
        assert 'token' not in res.data
        assert res.status_code == 404

    def test_invalid_otp_code_return_bad_request(
            self,
            otp_user,
            call_verify_code_token_endpoint,
            monkeypatch
    ):
        code_token_uuid = OtpDeviceToken.generate_token(otp_user.device)
        data = {'code_token': code_token_uuid, 'otp_code': 123456}
        monkeypatch.setattr(otp_user.device.__class__, 'verify_token', lambda _, __: False)
        res = call_verify_code_token_endpoint(data)
        assert res.status_code == 400
        assert 'token' not in res.data
