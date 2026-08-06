class AppException(Exception):
    # Base exception for the application
    status_code = 500
    default_message = "An unexpected error occurred."

    def __init__(self, message=None, errors=None):
        super().__init__(message)

        self.message = message or self.default_message
        self.errors = errors

class ValidationException(AppException):
    status_code = 400
    default_message = "Validation failed."

class AuthenticationException(AppException):
    status_code = 401
    default_message = "Authentication required."  

class PermissionDeniedException(AppException):
    status_code = 403
    default_message = "You do not have permission to perform this action."

class NotFoundException(AppException):
    status_code = 404
    default_message = "Requested resource was not found."   

class ConflictException(AppException):
    status_code = 409
    default_message = "Resource already exists."           
