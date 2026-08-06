from shared.exceptions import ValidationException
from shared.exceptions import AuthenticationException
from shared.exceptions import NotFoundException
from flask_bcrypt import check_password_hash, generate_password_hash
from auth.repository import AuthRepository
from modules.user.service import UserService
from auth.serializer import AuthSerializer
from flask_jwt_extended import create_access_token
from models import User, db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from auth.token_service import TokenService
from auth.mail_service import MailService


class AuthService:

    @staticmethod
    def signup(data):

        if AuthRepository.find_by_email(data["email"]):
            raise ValidationError(
                "Email already exists."
            )
        if AuthRepository.find_by_phone(data["phone"]):
            raise ValidationException(
                "Phone already exists."
            )

        data["password"] = generate_password_hash(
            data["password"]
        ).decode()

        user = User(**data)

        AuthRepository.save(user)

        UserService.create_default_profile(user)

        db.session.commit()

        verification_token = TokenService.generate_verification_token(user.email)

        MailService.send_verification(user, verification_token)

        token = create_access_token(identity=user.id, additional_claims={"role": user.role})

        return {
            "user": AuthSerializer.user(user),
            "access_token": token,
        }

    @staticmethod
    def login(data):

        user = AuthRepository.find_by_email(data["email"])

        if not user:
            raise AuthenticationException()
        # if not user.is_verified:
        #     raise AuthenticationException(
        #         "Please verify your email before logging in."
        #     )
        if not user.check_password(data["password"]):
            raise AuthenticationException()

        token = create_access_token(identity=user.id, additional_claims={"role": user.role})

        return {
            "user": AuthSerializer.user(user),
            "access_token": token,
        }

    @staticmethod
    def logout():
        ...

    @staticmethod
    def forgot_password(data):
        """Send a password reset link to the given email if a user exists."""
        email = data["email"]

        user = AuthRepository.find_by_email(email)

        # Always return success to avoid revealing whether an email is registered.
        if not user:
            return {"message": "If an account with that email exists, a password reset link has been sent."}

        reset_token = TokenService.generate_reset_token(user.email)

        MailService.send_password_reset(user, reset_token)

        return {"message": "If an account with that email exists, a password reset link has been sent."}

    @staticmethod
    def reset_password(data):
        """Verify the reset token and update the user's password."""
        token = data["token"]
        new_password = data["password"]

        try:
            email = TokenService.verify_reset_token(token)
        except Exception:
            raise ValidationException(
                "Invalid or expired reset token."
            )

        user = AuthRepository.find_by_email(email)

        if not user:
            raise NotFoundException(
                "User not found."
            )

        user.password = generate_password_hash(new_password).decode()

        db.session.commit()

        return {"message": "Password reset successfully. You can now sign in."}
