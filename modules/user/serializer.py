class UserSerializer:

    @staticmethod
    def profile(user):

        profile = None

        if user.role == "user":
            profile = user.user_profile

        elif user.role == "agent":
            profile = user.agent_profile

        elif user.role == "admin":
            profile = user.admin_profile

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_verified": user.is_verified,

            "profile": {
                "profile_picture": getattr(profile, "profile_picture", None),
                "bio": getattr(profile, "bio", None),
                "license_number": getattr(profile, "license_number", None),
                "agency_id": getattr(profile, "agency_id", None),
                "is_active": getattr(profile, "is_active", None),
            },

            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }