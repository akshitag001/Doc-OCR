import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from models.schemas import (
    ExtractionResult,
    HolderInfo,
    CredentialInfo,
    IssuerInfo,
)
from models.exceptions import DocumentQualityError
from storage.file_store import FileStore
from services.ocr_service import OCRService
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

# Global executor for background jobs (max 3 workers)
_executor = ThreadPoolExecutor(max_workers=3)
_ocr_service = OCRService()
_llm_service = LLMService()


async def submit_job(job_id: str, file_path: str, filename: str) -> None:
    """
    Submit a background job to process the uploaded file.
    Returns immediately; processing happens asynchronously.
    """
    try:
        # Mark job as processing
        result = ExtractionResult(
            id=job_id,
            status="processing",
            filename=filename,
            confidence={},
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        FileStore.save_result(job_id, result)
        
        # Submit to thread pool
        _executor.submit(_run_pipeline, job_id, file_path, filename)
        logger.info(f"Submitted job {job_id} for processing")
    except Exception as e:
        logger.error(f"Error submitting job {job_id}: {e}")


def _run_pipeline(job_id: str, file_path: str, filename: str) -> None:
    """
    Run the full OCR and extraction pipeline.
    This runs in a background thread.
    """
    try:
        logger.info(f"Starting pipeline for job {job_id}")
        
        # Step 1: Preprocess image
        logger.info(f"[{job_id}] Step 1: Preprocessing image...")
        try:
            preprocessed_path = _ocr_service.preprocess_image(file_path)
        except DocumentQualityError as e:
            logger.warning(f"[{job_id}] Preprocessing revealed quality issue: {e}")
            result = ExtractionResult(
                id=job_id,
                status="failed",
                filename=filename,
                confidence={},
                errorMessage=str(e),
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            FileStore.save_result(job_id, result)
            return
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            preprocessed_path = file_path
        
        # Step 2: Extract text (OCR)
        logger.info(f"[{job_id}] Step 2: Running OCR...")
        try:
            ocr_result = _ocr_service.extract_text(preprocessed_path)
            raw_text = ocr_result.get("raw_text", "")
            blocks = ocr_result.get("blocks", [])
            overall_confidence = ocr_result.get("overall_confidence", 0)
        except DocumentQualityError as e:
            logger.warning(f"[{job_id}] Document quality too low: {e}")
            result = ExtractionResult(
                id=job_id,
                status="failed",
                filename=filename,
                confidence={},
                errorMessage=str(e),
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            FileStore.save_result(job_id, result)
            return
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raw_text = ""
            blocks = []
            overall_confidence = 0
        
        if not raw_text or overall_confidence < 20:
            # OCR failed
            result = ExtractionResult(
                id=job_id,
                status="failed",
                filename=filename,
                confidence={},
                errorMessage="Document quality too low for OCR. Please upload a clearer image.",
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            FileStore.save_result(job_id, result)
            logger.warning(f"[{job_id}] OCR produced no text or very low confidence")
            return
        
        # Step 3: Extract entities using LLM
        logger.info(f"[{job_id}] Step 3: Extracting structured data...")
        try:
            extraction_data = _llm_service.extract_entities(raw_text, file_path, blocks)
        except Exception as e:
            logger.error(f"LLM extraction failed (retry): {e}")
            try:
                extraction_data = _llm_service.extract_entities(raw_text, file_path, blocks)
            except Exception as retry_error:
                logger.error(f"LLM extraction retry failed: {retry_error}")
                extraction_data = {}
        
        # Step 4: Build and save result
        logger.info(f"[{job_id}] Step 4: Saving results...")
        result = ExtractionResult(
            id=job_id,
            status="completed",
            filename=filename,
            holder=HolderInfo(**extraction_data.get("holder", {})),
            credential=CredentialInfo(**extraction_data.get("credential", {})),
            issuer=IssuerInfo(**extraction_data.get("issuer", {})),
            confidence=extraction_data.get("confidence", {}),
            rawText=raw_text,
            documentType=extraction_data.get("documentType"),
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        FileStore.save_result(job_id, result)
        logger.info(f"[{job_id}] Pipeline completed successfully")
        
    except DocumentQualityError as e:
        logger.error(f"[{job_id}] Document quality error: {e}")
        try:
            result = ExtractionResult(
                id=job_id,
                status="failed",
                filename=filename,
                confidence={},
                errorMessage=str(e),
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            FileStore.save_result(job_id, result)
        except Exception as save_error:
            logger.error(f"Failed to save error result: {save_error}")
    except Exception as e:
        logger.error(f"Pipeline error for {job_id}: {e}")
        # Save failed state
        try:
            result = ExtractionResult(
                id=job_id,
                status="failed",
                filename=filename,
                confidence={},
                errorMessage=str(e),
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            FileStore.save_result(job_id, result)
        except Exception as save_error:
            logger.error(f"Failed to save error result: {save_error}")
