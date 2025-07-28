from flask import jsonify
from exceptions import AppError

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
