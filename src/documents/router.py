from fastapi import APIRouter,Depends,File,HTTPException,UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User

from src.database.session import get_db


from src.documents.repository import DocumentRepository
from src.documents.service import DocumentService
from src.documents.schemas import DocumentResponse


router = APIRouter(prefix="/documents",tags=["documents"])

@router.post("/upload",response_model=DocumentResponse)
async def upload_document(file:UploadFile = File(...),current_user:User = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    repository = DocumentRepository(db)
    service = DocumentService(repository)

    try:
        result =  await service.uploade_document(file,current_user.id)
        return {
            "id":str(result.id),
            "filename":result.filename,
            "original_filename":result.original_filename,
            "file_size":result.file_size,
            "content_type":result.content_type,
            "status":result.status,
            "created_at":result.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))


@router.get("/{document_id}")
async def get_document_status(document_id:str,db:AsyncSession = Depends(get_db)):
    repository = DocumentRepository(db)
    document = await repository.get_by_id(document_id)
    try:
        return {
            "status":document.status
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Document not found")
    
@router.get("/analytics/summary")
async def analytics_summary(db:AsyncSession = Depends(get_db)):
    repository = DocumentRepository(db)
    service = DocumentService(repository)
    return await service.get_cached_analytics()


@router.get("/metrics/system")
async def system_metrics():
    # Simulate system metrics for demonstration
    return {
        "status": "Healthy",
        "service": "Enterprise KYC Platform",
        "version": "1.0.0"
    }

@router.get("/analytics/performance")
async def performance_metrics(db:AsyncSession = Depends(get_db)):
    repository = DocumentRepository(db)
    avg_time = await repository.average_processing_time()
    return {"average_processing_time": avg_time}