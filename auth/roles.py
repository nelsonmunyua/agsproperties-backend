# auth/roles.py

from auth.permissions import Permissions

ROLE_PERMISSIONS = {

    "admin": {

        Permissions.PROPERTY_VIEW,
        Permissions.PROPERTY_CREATE,
        Permissions.PROPERTY_UPDATE,
        Permissions.PROPERTY_DELETE,
        Permissions.PROPERTY_APPROVE,

        Permissions.AGENCY_VIEW,
        Permissions.AGENCY_CREATE,
        Permissions.AGENCY_UPDATE,
        Permissions.AGENCY_DELETE,

        Permissions.USER_VIEW,
        Permissions.USER_UPDATE,
        Permissions.USER_DELETE,

        Permissions.ADMIN_DASHBOARD,

    },

    "agent": {

        Permissions.PROPERTY_VIEW,
        Permissions.PROPERTY_CREATE,
        Permissions.PROPERTY_UPDATE,

        Permissions.MESSAGE_SEND,

        Permissions.APPOINTMENT_UPDATE,

    },

    "user": {

        Permissions.PROPERTY_VIEW,

        Permissions.FAVORITE_CREATE,
        Permissions.FAVORITE_DELETE,

        Permissions.APPOINTMENT_CREATE,

        Permissions.MESSAGE_SEND,

        Permissions.REVIEW_CREATE,

    }

}