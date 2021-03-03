import pytest
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    credentials = {
        'username': "John",
        'password': 'secret'
    }
    return get_user_model().objects.create_user(**credentials)


@pytest.fixture(scope='function', params=[TOTPDevice, StaticDevice])
def otp_user(user, request):
    device = request.param.objects.create(user=user, name='Default')
    user.device = device
    yield user


@pytest.fixture
def call_auth_endpoint(api_client):
    endpoint = '/api-token-auth-otp/'

    def _call_auth_endpoint(credentials):
        res = api_client.post(endpoint, credentials)
        return res
    return _call_auth_endpoint
