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
### First

```json
POST http://localhost:8000/api-token-auth-otp {"username": "John", "password": "secret"}
```
### Response
```json
{
    "StaticDevice": [
        {
            "name": "default",
            "code_token": "5e7518a2-d858-4f1b-976a-3d9540fe6c06"
        }
    ]
}
```

### Second
```json
POST http://localhost:8000/verify-code-token/ {"code_token": "5e7518a2-d858-4f1b-976a-3d9540fe6c06", "otp_code": "654321"}
```
### Response
```json
{"token": "<JWT Token>"}
```
