from models import User, db
from sqlalchemy.orm import Session

class AuthRepository:

    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()
        
    @staticmethod
    def find_by_phone(phone):
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def save(user):
        db.session.add(user)
        db.session.flush()

        return user
        




