from auth.resource import (
    SignupResource, LoginResource, ForgotPasswordResource, ResetPasswordResource
)
from auth.email_resource import VerifyEmailResource

def register_auth_routes(api):
    api.add_resource( SignupResource, "/signup")
    api.add_resource( LoginResource, "/login") 
    api.add_resource( VerifyEmailResource, "/verify-email")
    api.add_resource( ForgotPasswordResource, "/forgot-password")
    api.add_resource( ResetPasswordResource, "/reset-password")

