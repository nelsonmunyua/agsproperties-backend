from functools import wraps

from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request,
)

from shared.exceptions import (
    AuthenticationException,
    PermissionDeniedException,
)

# i will confirm if this import works
from modules.user import UserRepository

def permission_required(permission):
    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            user_id = get_jwt_identity()

            user = UserRepository.find_by_id(user_id)    


            if not user:
                raise AuthenticationException(
                    "User does not exist."
                )

            if not user.has_permission(permission):

                raise PermissionDeniedException(
                    f"Missing permission: {permission}"
                )
            return fn(*args, **kwargs)

        return wrapper
        
    return decorator            

