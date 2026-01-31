from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask import Flask


# Here is a custom decorator that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user is
# an administrator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if claims is None:
                return {"message":"Unauthorized request"}, 403
            if claims["role"] == "admin":
                return fn(*args, **kwargs)
            else:
                return {"message":"Unauthorized request"}, 403

        return decorator

    return wrapper