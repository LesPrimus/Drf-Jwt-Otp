from django_otp.models import Device
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebTokenView

from drf_jwt_otp.models import OtpDeviceToken
from drf_jwt_otp.serializers import JsonWebTokenOtpSerializer, VerifyCodeTokenSerializer


class JsonWebTokenOtpView(ObtainJSONWebTokenView):
    serializer_class = JsonWebTokenOtpSerializer


class VerifyCodeTokenView(ObtainJSONWebTokenView):
    serializer_class = VerifyCodeTokenSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    error_message = 'Not found'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code_token = serializer.validated_data.get("code_token")
        otp_code = serializer.validated_data.get("otp_code")
        device_persistent_id = self.get_device_id_from_token(code_token)
        if device_persistent_id:
            device = self.get_device_from_persistent_id(device_persistent_id)
            if device:
                if device.verify_token(otp_code):
                    self.delete_user_otp_device_tokens(device)
                    payload = self.get_response_data(device.user)
                    return Response(payload, status=status.HTTP_200_OK)
                else:
                    self.error_message = 'wrong otp code'
        return Response({'details': self.error_message}, status=status.HTTP_404_NOT_FOUND)

    @classmethod
    def get_device_id_from_token(cls, code_token):
        try:
            device_id = OtpDeviceToken.objects.get(uuid=code_token).device_persistent_id
        except OtpDeviceToken.DoesNotExist:
            device_id = None
        return device_id

    @classmethod
    def get_device_from_persistent_id(cls, persistent_id):
        try:
            device = Device.from_persistent_id(persistent_id)
        except Device.DoesNotExist:
            device = None
        return device

    @classmethod
    def get_response_data(cls, user):
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return {'token': token}

    @classmethod
    def delete_user_otp_device_tokens(cls, device: Device):
        OtpDeviceToken.objects.filter(user_id=device.user_id).delete()


verify_code_token_view = VerifyCodeTokenView.as_view()
