from fastapi import Request
from fastapi.responses import JSONResponse

from src.infrastructure.logging.logger import logger



class AppException(Exception):
    def __init__(self, status_code: int, message: str):
        self.message = message
        self.status_code = status_code

async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"Error occurred: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False,"error": exc.message}
    )