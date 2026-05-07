from fastapi import FastAPI
from .config.settings import settings


app = FastAPI(title=settings.APP_NAME)

@app.get("/")
async def root():
    return {
        "message": "Enterprise KYC Platform is up and running!!!!",
        "app": settings.APP_NAME,
        "env": settings.ENV
        }

