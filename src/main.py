from fastapi import FastAPI,Depends
from .config.settings import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.auth.router import router as auth_router

from src.documents.router import router as document_router
from src.infrastructure.logging.middleware import logging_middleware
from src.exceptions import AppException,app_exception_handler

app = FastAPI(title=settings.APP_NAME)

app.middleware("http")(logging_middleware)
app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth_router)
app.include_router(document_router)

@app.get("/")
async def health_check(db:AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))

    return {
        "message": "Enterprise KYC Platform is up and running!!!!",
        "app": settings.APP_NAME,
        "env": settings.ENV,
        "database":result.scalar()
        }

