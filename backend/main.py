import logging
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Document OCR API", version="1.0.0")

# Add CORS middleware (allow localhost:3000 for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)

# Mount uploads directory as static files
UPLOADS_DIR = Path("uploads")
if UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions globally."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize directories and check dependencies on startup."""
    logger.info("Starting Document OCR API...")
    
    # Create required directories
    UPLOADS_DIR.mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    logger.info("Created uploads and results directories")
    
    # Check for tesseract (optional warning, don't crash)
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        logger.info("Tesseract is installed and available")
    except Exception:
        logger.warning(
            "Tesseract is not installed or not found. "
            "OCR will fall back to EasyOCR. Install with: apt-get install tesseract-ocr"
        )
    
    logger.info("API startup complete. Ready to accept requests.")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
