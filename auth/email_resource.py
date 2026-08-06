from flask import request
from flask_restful import Resource
from auth.token_service import TokenService
from models import User, db

class VerifyEmailResource(Resource):

    def get(self):
        token = request.args.get("token")

        try:
            email = TokenService.verify_verification_token(token)
        except Exception:
            return {"message": "Invalid or expired token"}, 400

        user = User.query.filter_by(email=email).first()   

        if not user:
            return {"message": "User not found"}, 404

        if user.is_verified:
            return {"message": "Email already verified"}, 200

        user.is_verified = True
        db.session.commit() 

        return {"message": "Email verified successfully"}, 200