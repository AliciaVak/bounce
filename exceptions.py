from typing import Optional


class AppError(Exception):
    status_code = 500

    def __init__(self, message: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message or "Internal Server Error"
        self.status_code = status_code or self.__class__.status_code

    def to_dict(self):
        return {'error': self.message}

class BadRequestError(AppError):
    status_code = 400

class InvalidInputError(AppError):
    status_code = 422
