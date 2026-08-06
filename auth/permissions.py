# auth/permissions.py

class Permissions:

    # Property
    PROPERTY_VIEW = "property:view"
    PROPERTY_CREATE = "property:create"
    PROPERTY_UPDATE = "property:update"
    PROPERTY_DELETE = "property:delete"
    PROPERTY_APPROVE = "property:approve"

    # Agency
    AGENCY_VIEW = "agency:view"
    AGENCY_CREATE = "agency:create"
    AGENCY_UPDATE = "agency:update"
    AGENCY_DELETE = "agency:delete"

    # User
    USER_VIEW = "user:view"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Reviews
    REVIEW_CREATE = "review:create"
    REVIEW_DELETE = "review:delete"

    # Favorites
    FAVORITE_CREATE = "favorite:create"
    FAVORITE_DELETE = "favorite:delete"

    # Appointments
    APPOINTMENT_CREATE = "appointment:create"
    APPOINTMENT_UPDATE = "appointment:update"
    APPOINTMENT_CANCEL = "appointment:cancel"

    # Messaging
    MESSAGE_SEND = "message:send"

    # Dashboard
    ADMIN_DASHBOARD = "admin:dashboard"