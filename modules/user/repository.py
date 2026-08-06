# modules/user/repository
from models import db, User, AgentProfile
from sqlalchemy.orm import joinedload


class UserRepository:

    @staticmethod
    def get_agent_profile(user_id):
        return AgentProfile.query.filter_by(user_id=user_id).first()

    @staticmethod
    def get_agent(agent_id):
        return AgentProfile.query.get(agent_id)   

    @staticmethod
    def save_profile(profile):
        
        db.session.add(profile)
        return profile

    # method to query all user-profiles
    @staticmethod
    def get(user_id):
        return (
            User.query
            .options(
                joinedload(User.user_profile),
                joinedload(User.agent_profile),
                joinedload(User.admin_profile)
            )
            .filter(User.id == user_id)
            .first()
        )   