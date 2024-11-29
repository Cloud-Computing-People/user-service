from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        await self.log_request(request)

        response = await call_next(request)

        await self.log_response(response, start_time, request)

        return response

    async def log_request(self, request: Request):
        logging.info(f"[{request.state.request_id}] Incoming request: {request.method} {request.url}")

        if request.method in ["POST", "PUT"]:
            request_body = await request.body()
            logging.info(f"Request body: {request_body.decode('utf-8')}")

    async def log_response(self, response, start_time, request):
        process_time = time.time() - start_time
        response_body = b""
        if isinstance(response, JSONResponse):
            response_body = response.body
            logging.info(f"Response body: {response_body.decode('utf-8')}")

        logging.info(f"[{request.state.request_id}]Response status: {response.status_code} | Time taken: {process_time:.4f}s")

        if response.status_code >= 400:
            error_message = f"Error {response.status_code}: {response_body.decode('utf-8') if response_body else 'No response body'}"
            logging.error(error_message)


class OverallMiddleware:
    def __init__(self, app):
        self.app = RequestIDMiddleware(LoggingMiddleware(app))
    
    def __call__(self, scope, receive, call_next):
        return self.app(scope, receive, call_next)
    