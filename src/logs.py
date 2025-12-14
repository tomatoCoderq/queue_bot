from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
import time


def init_logging(app: FastAPI) -> None:
    logger.add("logs/app.log",
               rotation="100 MB",
               retention="14 days",
               compression="zip",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
               level="DEBUG"
               )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        # Start timer
        start_time = time.time()

        logger.info(
            f"Request: {request.method} {request.url} | "
            f"Body: {await request.body() if request.method in ['POST', 'PUT', 'PATCH'] else 'None'} | "
            f"Query Params: {dict(request.query_params) if request.query_params else 'None'}"
        )

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            f"Response: Status Code {response.status_code} | "
            f"Duration: {duration:.4f} seconds"
        )

        return response
