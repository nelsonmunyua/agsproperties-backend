from shared.exceptions import ValidationException

class SignupSchema:

    required_fields = [
        "first_name",
        "last_name",
        "phone",
        "email",
        "password",
        "role",
    ]

    # Public signup is restricted to "user" role only.
    # Admin and agent accounts must be created by an existing admin.
    ALLOWED_ROLES = {"user"}

    MIN_PASSWORD_LENGTH = 8

    @staticmethod
    def validate(data):
        
        if not data:
            raise ValidationException(
                "Request body is required"
            )

        # Role checking
        role = data.get("role", "").strip().lower()

        if role not in SignupSchema.ALLOWED_ROLES:
            raise ValidationException(
                "Invalid role."
            )    
        # Required fields
        for field in SignupSchema.required_fields:

            value = data.get(field)
            if value is None or str(value).strip() == "":
                raise ValidationException(
                    f"{field.replace('_', ' ').title()} is required."
                ) 
        # Password strength check
        password = data["password"]
        if len(password) < SignupSchema.MIN_PASSWORD_LENGTH:
            raise ValidationException(
                f"Password must be at least {SignupSchema.MIN_PASSWORD_LENGTH} characters."
            )

        # Normalize
        return {
            "first_name": data["first_name"].strip(),
            "last_name": data["last_name"].strip(),
            "phone": data["phone"].strip(),
            "email": data["email"].strip().lower(),
            "password": password,
            "role": "user",  # force role to "user" regardless of input
        } 


class LoginSchema:
    
    @staticmethod
    def validate(data):
        
        if not data:
            raise ValidationException(
                "Request body is required"
            )
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise ValidationException(
                "Email is required."
            )    
        if not password:
            raise ValidationException(
                "Password is required."
            )    
        return {
            "email": email.strip().lower(),
            "password": password,
        }    


class ForgotPasswordSchema:
    """Validates the email submitted for a password reset request."""

    @staticmethod
    def validate(data):
        if not data:
            raise ValidationException(
                "Request body is required"
            )

        email = data.get("email")

        if not email or str(email).strip() == "":
            raise ValidationException(
                "Email is required."
            )

        return {
            "email": email.strip().lower(),
        }


class ResetPasswordSchema:
    """Validates the token and new password for a password reset."""

    MIN_PASSWORD_LENGTH = 8

    @staticmethod
    def validate(data):
        if not data:
            raise ValidationException(
                "Request body is required"
            )

        token = data.get("token")
        password = data.get("password")

        if not token or str(token).strip() == "":
            raise ValidationException(
                "Token is required."
            )

        if not password or str(password).strip() == "":
            raise ValidationException(
                "New password is required."
            )

        if len(password) < ResetPasswordSchema.MIN_PASSWORD_LENGTH:
            raise ValidationException(
                f"Password must be at least {ResetPasswordSchema.MIN_PASSWORD_LENGTH} characters."
            )

        return {
            "token": token.strip(),
            "password": password,
        }
