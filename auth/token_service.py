from itsdangerous import URLSafeTimedSerializer
from flask import current_app


class TokenService:

 # setting up tokens
    @staticmethod
    def serializer():
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])  

    @staticmethod
    def generate_verification_token(email):
        return TokenService.serializer().dumps(
            email,
            salt="email-verification"
        ) 

    @staticmethod
    def verify_verification_token(token, max_age=3600):
        return TokenService.serializer().loads(
            token,
            salt="email-verification",
            max_age=max_age
        )

    @staticmethod
    def generate_reset_token(email):
        return TokenService.serializer().dumps(
            email,
            salt="password-reset"
        )

    @staticmethod
    def verify_reset_token(token, max_age=900):
        return TokenService.serializer().loads(
            token,
            salt="password-reset",
            max_age=max_age
        )
