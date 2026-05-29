import json
import logging
import os
import uuid
from pathlib import Path
from typing import Optional, List
from models.schemas import ExtractionResult
from fastapi import UploadFile
from datetime import datetime

logger = logging.getLogger(__name__)

DEFAULT_UPLOADS_DIR = Path("uploads")
DEFAULT_RESULTS_DIR = Path("results")


class FileStore:
    """Handle file storage for uploads and results."""

    @staticmethod
    def _uploads_dir() -> Path:
        return Path(os.getenv("UPLOADS_DIR", str(DEFAULT_UPLOADS_DIR)))

    @staticmethod
    def _results_dir() -> Path:
        return Path(os.getenv("RESULTS_DIR", str(DEFAULT_RESULTS_DIR)))
    
    @staticmethod
    def _ensure_dirs():
        """Ensure upload and results directories exist."""
        FileStore._uploads_dir().mkdir(exist_ok=True)
        FileStore._results_dir().mkdir(exist_ok=True)
    
    @staticmethod
    async def save_upload(file: UploadFile) -> str:
        """
        Save uploaded file to disk with UUID-based name.
        Returns the relative path to the saved file.
        """
        FileStore._ensure_dirs()
        
        try:
            # Generate UUID filename preserving extension
            file_ext = Path(file.filename or "").suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = FileStore._uploads_dir() / unique_filename
            
            # Write file to disk
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            logger.info(f"Saved upload to {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving upload: {e}")
            raise
    
    @staticmethod
    def save_result(job_id: str, result: ExtractionResult) -> None:
        """Save extraction result to JSON file."""
        FileStore._ensure_dirs()
        
        try:
            result_path = FileStore._results_dir() / f"{job_id}.json"
            with open(result_path, "w") as f:
                json.dump(result.model_dump(mode="json"), f, indent=2, default=str)
            logger.info(f"Saved result to {result_path}")
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            raise
    
    @staticmethod
    def get_result(job_id: str) -> Optional[ExtractionResult]:
        """Retrieve extraction result from JSON file."""
        try:
            result_path = FileStore._results_dir() / f"{job_id}.json"
            if not result_path.exists():
                return None
            
            with open(result_path, "r") as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            if isinstance(data.get("createdAt"), str):
                data["createdAt"] = datetime.fromisoformat(data["createdAt"])
            if isinstance(data.get("updatedAt"), str):
                data["updatedAt"] = datetime.fromisoformat(data["updatedAt"])
            
            return ExtractionResult(**data)
        except Exception as e:
            logger.error(f"Error retrieving result: {e}")
            return None
    
    @staticmethod
    def list_results() -> List[ExtractionResult]:
        """List all results sorted by creation date (newest first)."""
        FileStore._ensure_dirs()
        
        try:
            results = []
            for result_file in FileStore._results_dir().glob("*.json"):
                with open(result_file, "r") as f:
                    data = json.load(f)
                
                # Convert datetime strings
                if isinstance(data.get("createdAt"), str):
                    data["createdAt"] = datetime.fromisoformat(data["createdAt"])
                if isinstance(data.get("updatedAt"), str):
                    data["updatedAt"] = datetime.fromisoformat(data["updatedAt"])
                
                results.append(ExtractionResult(**data))
            
            # Sort by createdAt descending
            results.sort(key=lambda r: r.createdAt, reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error listing results: {e}")
            return []
    
    @staticmethod
    def delete_upload(file_path: str) -> None:
        """Delete uploaded file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted upload: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting upload: {e}")
    
    @staticmethod
    def delete_result(job_id: str) -> None:
        """Delete result JSON file."""
        try:
            result_path = FileStore._results_dir() / f"{job_id}.json"
            if result_path.exists():
                result_path.unlink()
                logger.info(f"Deleted result: {job_id}")
        except Exception as e:
            logger.error(f"Error deleting result: {e}")
