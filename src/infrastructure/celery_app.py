from celery import Celery
from src.config.settings import settings

celery_app = Celery(
    "enterprise_kyc",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
celery_app.autodiscover_tasks(["src.documents"])
