# shared/error_handlers.py
import traceback
from flask import current_app
from shared.exceptions import AppException


def register_error_handlers(app):

    @app.errorhandler(AppException)
    def handle_application_error(error):
        response = {
            "success": False,
            "message": error.message
        }
        if error.errors:
            response["errors"] = error.errors
        return response, error.status_code

    @app.errorhandler(Exception)
    def handle_unhandled_error(error):
        current_app.logger.error(f"Unhandled error: {error}", exc_info=True)
        return {
            "success": False,
            "message": "An unexpected internal error occurred."
        }, 500
