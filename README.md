Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

celery -A src.infrastructure.celery_app worker --loglevel=info --pool=solo