import time
from fastapi import Request

from src.infrastructure.logging.logger import logger


async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incomming request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"Completed request: {request.method} {request.url} - Status code: {response.status_code} - Process time: {process_time:.2f} seconds"
    )

    return response
