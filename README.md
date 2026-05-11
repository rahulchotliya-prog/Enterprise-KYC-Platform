Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

celery -A src.infrastructure.celery_app worker --loglevel=info --pool=solo


docker compose exec api alembic upgrade head

docker compose exec postgres_db psql -U postgres -d enterprise_kyc

\dt:
    documents
    users
    alembic_version


\q

docker compose exec api alembic revision --autogenerate -m "initial migration"

docker compose exec api alembic upgrade head