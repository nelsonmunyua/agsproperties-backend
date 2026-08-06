from modules.user.resource import UserResource

def register_user_routes(api):
    api.add_resource( UserResource, "/profile")