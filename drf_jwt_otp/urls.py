from django.urls import path

from drf_jwt_otp.views import JsonWebTokenOtpView, VerifyCodeTokenView

urlpatterns = [
    path('api-token-auth-otp/', JsonWebTokenOtpView.as_view()),
    path('verify-code-token/', VerifyCodeTokenView.as_view()),
]
