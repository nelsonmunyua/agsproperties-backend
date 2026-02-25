from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify


# Here is a custom decorator that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user is
# an administrator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()

                if claims is None:
                    return {"message": "Unauthorized request"}, 403
                if claims.get("role") == "admin":
                    return fn(*args, **kwargs)
                else:
                    return {"message": "Unauthorized request - Admin access required"}, 403
            except Exception as e:
                return {"message": "Invalid or missing token", "error": str(e)}, 401

        return decorator

    return wrapper

def agent_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()

                if claims is None:
                    return {"message": "Unauthorized request"}, 403
                if claims.get("role") == "agent":
                    return fn(*args, **kwargs)
                else:
                    return {"message": "Unauthorized request - Agent access required"}, 403
            except Exception as e:
                return {"message": "Invalid or missing token", "error": str(e)}, 401
        return decorator    
    return wrapper

def user_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()

                if claims is None:
                    return {"message": "Unauthorized request"}, 403
                if claims.get("role") == "user":
                    return fn(*args, **kwargs)
                else:
                    return {"message": "Unauthorized request - User access required"}, 403
            except Exception as e:
                return {"message": "Invalid or missing token", "error": str(e)}, 401
        return decorator    
    return wrapper
