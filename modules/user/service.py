# modules/user/service.py
from modules.user.repository import UserRepository
from models import (db, UserProfile, AgentProfile, AdminProfile, User)
from shared.exceptions import ValidationException
from modules.user.exceptions import UserNotFound
from modules.user.serializer import UserSerializer

class UserService:
    def resolve_property_owner(actor, data):

        if actor.role == "admin":
            return UserRepository.get_agent(data["agent_id"])
        return UserRepository.get_agent_profile(actor.id)  

    # create user_profile
    @staticmethod
    def create_default_profile(user: User):

        if user.role == "user":
            profile = UserProfile(user_id=user.id)
        elif user.role == "agent":
            profile = AgentProfile(user_id=user.id,
            # should update the license field to null in the models
            license_number=f"TEMP-{user.id}")    
        elif user.role == "admin":
            profile = AdminProfile(user_id=user.id, is_active=True)
        else:
            raise ValidationException(
                "Invalid user role."
            )

        return UserRepository.save_profile(profile)  

    @staticmethod
    def get_profile(user_id):
        
        user = UserRepository.get(user_id)

        if not user:
            raise UserNotFound()

        return UserSerializer.profile(user)    


