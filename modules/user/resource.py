from flask_restful import Resource
from modules.user.service import UserService
from flask_jwt_extended import current_user


class UserResource(Resource):
    def get(self):
        return UserService.get_profile(current_user), 200
