import re
from pathlib import Path
from fastapi import HTTPException, UploadFile

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def sanitize_filename(filename: str) -> str:
    """Remove special characters from filename, keep only alphanumeric and common punctuation."""
    normalized = filename.replace("\\", "/")
    parts = [p for p in normalized.split("/") if p not in ("", ".", "..")]
    base_name = "_".join(parts) if parts else "upload"
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", base_name)
    sanitized = re.sub(r"_+", "_", sanitized).lstrip("._")
    return sanitized or "upload"


async def validate_upload(file: UploadFile) -> None:
    """
    Validate file type, extension, and size.
    Raises HTTPException if validation fails.
    """
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # Check extension
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024:.0f}MB limit"
        )
    
    # Reset file pointer
    await file.seek(0)
