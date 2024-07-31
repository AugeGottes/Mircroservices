from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import uuid

def generate_error_id():
    return str(uuid.uuid4())

class BadRequest(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class NotFound(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class MethodNotAllowed(Exception):
    def __init__(self, detail: str):
        self.detail = detail

async def bad_request_handler(request: Request, exc: BadRequest):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Bad Request",
            "message": str(exc.detail),
            "status_code": 400,
            "description": "The server cannot process the request due to a client error.",
            "details": {
                "possible_reasons": [
                    "Missing required fields in the request body",
                    "Invalid data format",
                    "Incorrect parameter types"
                ],
                "suggestion": "Please check your request payload and parameters for any irregularity."
            }
        }
    )

async def not_found_handler(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc.detail),
            "status_code": 404,
            "description": "The requested resource could not be found on the server.",
            "details": {
                "possible_reasons": [
                    "The resource has been deleted",
                    "The resource never existed",
                    "You might have mistyped the URL"
                ],
                "suggestion": "Please verify the URL and try again"
            }
        }
    )

async def method_not_allowed_handler(request: Request, exc: MethodNotAllowed):
    return JSONResponse(
        status_code=405,
        content={
            "error": "Method Not Allowed",
            "message": "The method is not allowed for the requested URL",
            "status_code": 405,
            "description": "The HTTP method used is not supported for this resource.",
            "details": {
                "suggestion": "Please check the API documentation for the correct HTTP method to use for this endpoint."
            }
        }
    )

async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500,
            "description": "The server encountered an unexpected condition that prevented it from fulfilling the request.",
            "details": {
                "possible_reasons": [
                    "Server misconfiguration",
                    "Unexpected exception in the application code",
                    "Database connection issues"
                ],
                "suggestion": "Please try again later. If the problem persists, contact the server administrator.",
                "error_id": generate_error_id()
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Unexpected Error",
            "message": str(exc),
            "status_code": 500,
            "description": "An unexpected error occurred while processing your request.",
            "details": {
                "error_type": type(exc).__name__,
                "suggestion": "Please report this error to the server administrator with the details provided.",
                "error_id": generate_error_id()
            }
        }
    )

def register_error_handlers(app: FastAPI):
    app.add_exception_handler(BadRequest, bad_request_handler)
    app.add_exception_handler(NotFound, not_found_handler)
    app.add_exception_handler(MethodNotAllowed, method_not_allowed_handler)
    app.add_exception_handler(Exception, generic_exception_handler)