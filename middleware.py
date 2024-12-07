from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException
import logging
import time
import uuid

from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time
import uuid
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_request
from fastapi.responses import JSONResponse

load_dotenv()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

        token_header = request.headers.get("authorization")

        if not token_header:
            return JSONResponse({"message": "No token provided"}, status_code=403)

        token = token_header.split(" ")[1]
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(
                token, google_auth_request.Request(), client_id
            )

        except ValueError:
            # Invalid token
            return JSONResponse({"message": "Invalid token"}, status_code=403)

        response = await call_next(request)
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s"
)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        await self.log_request(request)

        response = await call_next(request)

        await self.log_response(response, start_time, request)

        return response

    async def log_request(self, request: Request):
        logging.info(
            f"[{request.state.request_id}] Incoming request: {request.method} {request.url}"
        )

        if request.method in ["POST", "PUT"]:
            request_body = await request.body()
            logging.info(f"Request body: {request_body.decode('utf-8')}")

    async def log_response(self, response, start_time, request):
        process_time = time.time() - start_time
        response_body = b""
        if isinstance(response, JSONResponse):
            response_body = response.body
            logging.info(f"Response body: {response_body.decode('utf-8')}")

        logging.info(
            f"[{request.state.request_id}]Response status: {response.status_code} | Time taken: {process_time:.4f}s"
        )

        if response.status_code >= 400:
            error_message = f"Error {response.status_code}: {response_body.decode('utf-8') if response_body else 'No response body'}"
            logging.error(error_message)


class OverallMiddleware:
    def __init__(self, app):
        self.app = AuthMiddleware(RequestIDMiddleware(LoggingMiddleware(app)))

    def __call__(self, scope, receive, call_next):
        return self.app(scope, receive, call_next)
    

async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error(f"[{request.state.request_id}] HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logging.error(f"[{request.state.request_id}] Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An error occured: " + str(exc)},
    )
