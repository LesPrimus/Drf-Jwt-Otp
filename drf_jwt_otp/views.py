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
    error_status = status.HTTP_404_NOT_FOUND

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code_token = serializer.validated_data.get("code_token")
        otp_code = serializer.validated_data.get("otp_code")
        device_token = OtpDeviceToken.get_instance_from_uuid(code_token)
        if device_token and device_token.is_valid():
            device = Device.from_persistent_id(device_token.device_persistent_id)
            if device:
                if device.verify_token(otp_code):
                    OtpDeviceToken.delete_user_instances(device.user_id)
                    payload = self.get_response_data(device.user)
                    return Response(payload, status=status.HTTP_200_OK)
                else:
                    self.error_message = 'wrong otp code'
                    self.error_status = status.HTTP_400_BAD_REQUEST
        return Response({'details': self.error_message}, status=self.error_status)

    @classmethod
    def get_response_data(cls, user):
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return {'token': token}


verify_code_token_view = VerifyCodeTokenView.as_view()
