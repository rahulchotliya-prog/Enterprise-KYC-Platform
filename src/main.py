import asyncio
import json

from fastapi import FastAPI, Depends
from .config.settings import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import get_db
from src.auth.router import router as auth_router

from src.documents.router import router as document_router
from src.infrastructure.logging.middleware import logging_middleware
from src.infrastructure.redis import redis_client
from src.infrastructure.websocket.manager import manager
from src.exceptions import AppException, app_exception_handler

app = FastAPI(title=settings.APP_NAME)

app.middleware("http")(logging_middleware)
app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth_router)
app.include_router(document_router)


async def document_notification_listener() -> None:
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("document_notifications")
    app.state.pubsub = pubsub

    try:
        async for message in pubsub.listen():
            if not message or message.get("type") != "message":
                continue

            try:
                payload = json.loads(message["data"])
                user_id = payload.get("user_id")
                if user_id:
                    await manager.send_personal_message(user_id, payload)
            except Exception as exc:
                print(f"Failed to forward notification: {exc}")
    except asyncio.CancelledError:
        pass


@app.on_event("startup")
async def startup_event() -> None:
    app.state.notification_task = asyncio.create_task(document_notification_listener())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    notification_task = getattr(app.state, "notification_task", None)
    if notification_task:
        notification_task.cancel()
        try:
            await notification_task
        except asyncio.CancelledError:
            pass

    pubsub = getattr(app.state, "pubsub", None)
    if pubsub:
        await pubsub.unsubscribe("document_notifications")
        await pubsub.close()


@app.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))

    return {
        "message": "Enterprise KYC Platform is up and running!!!!",
        "app": settings.APP_NAME,
        "env": settings.ENV,
        "database": result.scalar(),
    }
