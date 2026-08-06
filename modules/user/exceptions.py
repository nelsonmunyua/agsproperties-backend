from shared.exceptions import NotFoundException

class UserNotFound(NotFoundException):
    default_message = "User not found."
