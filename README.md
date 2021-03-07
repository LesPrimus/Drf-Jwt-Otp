# Testing integration of drf-otp package into drf-jwt.
- https://django-otp-official.readthedocs.io/en/stable/
- https://styria-digital.github.io/django-rest-framework-jwt/
## Settings
drf-jwt entrypoint
```python
JWT_AUTH = { 'JWT_RESPONSE_PAYLOAD_HANDLER': 'drf_jwt_otp.utils.jwt_create_response_otp_payload' }
```
Callable used to determine if user is otp.
```python
USER_OTP_ENABLED = 'drf_jwt_otp.utils.user_otp_enabled'
```
