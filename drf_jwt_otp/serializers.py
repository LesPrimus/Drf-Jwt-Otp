from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer

class JsonWebTokenOtpSerializer(JSONWebTokenSerializer): # noqa
    pass


class VerifyCodeTokenSerializer(serializers.Serializer): # noqa
    code_token = serializers.UUIDField()
    otp_code = serializers.CharField()
