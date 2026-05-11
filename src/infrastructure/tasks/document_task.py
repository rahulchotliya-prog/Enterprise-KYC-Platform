from src.infrastructure.celery_app import celery_app
import asyncio
from sqlalchemy import select, update
from src.database.session import AsyncSessionLocal
from src.documents.models import Document
from src.documents.constants import DocumentStatus
import time
from src.documents.utils import simulate_ocr_extraction, validate_extracted_data
import json
from src.infrastructure.redis import get_redis_client
from src.infrastructure.logging.logger import logger

# @celery_app.task
@celery_app.task(
    name="src.infrastructure.tasks.document_task",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    bind=True,
)
def process_document_task(self, document_id: str):

    # print(f"Processing document with id: {document_id}")
    logger.info(f"Processing document with id: {document_id}")
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # try:
    #     loop.run_until_complete(process_document(document_id))
    # finally:
    #     loop.close()
    try:
        asyncio.run(process_document(document_id))
    except Exception as e:
        logger.error(f"Error processing document with id: {document_id}, error: {e}")
        logger.info(
            f"Retrying document with id: {document_id}, attempt: {self.request.retries + 1}"
        )
        self.retry(exc=e, countdown=5)

        # Optionally, you can mark the document as failed in the database here
    # asyncio.run(process_document(document_id))
    # asyncio.sleep(5)
    # print(f"Document with id: {document_id} processed")
    logger.info(f"Document with id: {document_id} processed")

    return {"status": "completed"}


async def process_document(document_id: str):
    async with AsyncSessionLocal() as db:
        start_time = time.time()
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=DocumentStatus.PROCESSING)
        )
        await db.commit()
        # await redis_client.delete("analytics_summary")
        # await redis_client.delete("analytics_summary")

        # print("Processing Started")
        logger.info("Processing Started")
        document_query = await db.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        document = (
            document_query.scalar_one()
        )

        user_id = str(document.user_id)
        print(f"User ID: {user_id}")
        redis_client = get_redis_client()
        await redis_client.publish(
            "document_notifications",
            json.dumps(
                {
                    "user_id": user_id,
                    "event": "document_processing",
                    "document_id": document_id,
                    "status": "PROCESSING",
                }
            ),
        )
        await asyncio.sleep(5)

        # await db.execute(
        #     update(Document)
        #     .where(Document.id == document_id)
        #     .values(
        #         status=DocumentStatus.VERIFIED
        #     )
        # )
        extracted_data = simulate_ocr_extraction()

        is_valid = validate_extracted_data(extracted_data)

        processing_time = int(time.time() - start_time)
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(
                status=DocumentStatus.VERIFIED if is_valid else DocumentStatus.FAILED,
                extracted_data=extracted_data,
                processing_time=processing_time,
                failure_reason=None if is_valid else "Data validation failed",
            )
        )
        await db.commit()
        redis_client = get_redis_client()
        await redis_client.publish(
            "document_notifications",
            json.dumps(
                {
                    "user_id": user_id,
                    "event": "document_completed",
                    "document_id": document_id,
                    "status": "VERIFIED",
                }
            ),
        )
        # print(f"Processing time: {processing_time} seconds")
        logger.info(f"Processing time: {processing_time} seconds")
        try:
            # await redis_client.delete("analytics_summary")
            redis_client = get_redis_client()
            await redis_client.delete("analytics_summary")
            # print("Deleted analytics summary cache")
            logger.info("Deleted analytics summary cache")
        except Exception as e:
            logger.error(f"Error occurred while deleting analytics summary: {e}")
        # print("Processing Completed")
        logger.info("Processing Completed")
