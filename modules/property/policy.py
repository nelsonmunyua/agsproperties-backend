from auth.permissions import Permissions
from shared.exceptions import PermissionDeniedException

class PropertyPolicy:
    #Handles all property authorization rules
    @staticmethod
    def authorize_create(user):
        # Raise an exception if the user cannot create properties
        if not user.has_permission(Permissions.PROPERTY_CREATE):
            raise PermissionDeniedException(
                "You do not have permission to create properties."
            ) 

    @staticmethod
    def authorize_update(user, property):

        if not user.has_permission(Permissions.PROPERTY_UPDATE):
            raise PermissionDeniedException(
                "Missing update permission."
            )      

        if user.role == "admin":
            return

        if property.agent.user_id != user.id:
            raise PermissionDeniedException(
                "You can only update your own properties."
            )          

    @staticmethod
    def authorize_delete(user, property):

        if not user.has_permission(Permissions.PROPERTY_DELETE):
            raise PermissionDeniedException()

        if user.role == "admin":
            return

        if property.agent.user_id != user.id:
            raise PermissionDeniedException(
                "Cannot delete another agent's property."
            )     

    @staticmethod
    def authorize_view(user, property):

        if property.status == "approved":
            return
        if user.role == "admin":
            return
        if user.role == "agent":
            return
        if user.role == "user":
            return 

        # if property.agent.user_id == user.id:
        #     return

        raise PermissionDeniedException(
            "You cannot view this property."
        )                               