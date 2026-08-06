from flask_restful import Resource
from auth.schema import SignupSchema
from auth.schema import LoginSchema
from auth.schema import ForgotPasswordSchema
from auth.schema import ResetPasswordSchema
from auth.service import AuthService
from flask import request
from flask_jwt_extended import jwt_required

class SignupResource(Resource):

    def post(self):

        data = SignupSchema.validate(request.get_json())

        response = AuthService.signup(data)

        return response, 201

class LoginResource(Resource):

    def post(self):

        data = LoginSchema.validate(request.get_json()) 

        response = AuthService.login(data)

        return response, 201

class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        return AuthService.logout(current_user)

class ForgotPasswordResource(Resource):

    def post(self):

        data = ForgotPasswordSchema.validate(request.get_json())

        response = AuthService.forgot_password(data)

        return response, 200

class ResetPasswordResource(Resource):

    def post(self):

        data = ResetPasswordSchema.validate(request.get_json())

        response = AuthService.reset_password(data)

        return response, 200
