from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time

# Setup basic logging with a cleaner format
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        await self.log_request(request)

        response = await call_next(request)

        await self.log_response(response, start_time)

        return response

    async def log_request(self, request: Request):
        query_params = request.query_params
        logging.info(f"Incoming request: {request.method} {request.url}")

        if request.method in ["POST", "PUT"]:
            request_body = await request.body()
            logging.info(f"Request body: {request_body.decode('utf-8')}")

    async def log_response(self, response, start_time):
        process_time = time.time() - start_time
        response_body = b""
        if isinstance(response, JSONResponse):
            response_body = response.body
            logging.info(f"Response body: {response_body.decode('utf-8')}")

        logging.info(f"Response status: {response.status_code} | Time taken: {process_time:.4f}s")

        if response.status_code >= 400:
            error_message = f"Error {response.status_code}: {response_body.decode('utf-8') if response_body else 'No response body'}"
            logging.error(error_message)
