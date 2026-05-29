import logging
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from utils.validation import validate_upload
from storage.file_store import FileStore
from services.job_runner import submit_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/process", status_code=202)
async def process_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    Returns job_id for polling results.
    """
    try:
        # Validate upload
        await validate_upload(file)
        
        # Save file to disk
        file_path = await FileStore.save_upload(file)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Submit background job
        await submit_job(job_id, file_path, file.filename or "document")
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Processing started"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/{id}/result")
async def get_document_result(id: str):
    """
    Get extraction result for a specific job.
    """
    try:
        result = FileStore.get_result(id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving result: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("")
async def list_documents():
    """
    List all processed documents.
    """
    try:
        results = FileStore.list_results()
        return results
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.delete("/{id}", status_code=204)
async def delete_document(id: str):
    """
    Delete a document and its results.
    """
    try:
        result = FileStore.get_result(id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        
        # Delete uploaded file
        from pathlib import Path
        # The file path is stored in result, but we'd need to track it
        # For now, we'll just delete the result
        FileStore.delete_result(id)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
