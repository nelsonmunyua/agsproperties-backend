from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request,
)

from models import User


class CurrentUserService:

    @staticmethod
    def get():
        verify_jwt_in_request()

        user = User.query.get(get_jwt_identity())

        if not user:
            raise Exception("Authenticated user not found.")

        return user