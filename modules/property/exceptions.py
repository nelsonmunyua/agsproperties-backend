from shared.exceptions import (NotFoundException, ValidationException)

class PropertyNotFound(NotFoundException):
    default_message = "Property not found."

class InvalidPropertyData(ValidationException):
    default_message = "Invalid property information."    