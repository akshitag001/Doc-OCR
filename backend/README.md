# Document OCR & Extraction Backend

FastAPI-based backend for processing documents with OCR and extracting structured data using AI.

## Setup

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit `.env` and set:
- `GEMINI_API_KEY`: Your Gemini API key (for LLM extraction)
- `MAX_FILE_SIZE_MB`: Maximum upload size in MB (default: 10)
- `UPLOADS_DIR`: Directory for uploaded files (default: uploads/)
- `RESULTS_DIR`: Directory for JSON results (default: results/)

### 3. Start Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Server will be available at `http://localhost:8000`

## API Endpoints

### 1. Upload & Process Document
```
POST /api/documents/process
Content-Type: multipart/form-data

Request:
- file: <binary file>

Response (202):
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Processing started"
}
```

**Supported formats:**
- `.jpg`, `.jpeg`, `.png` (images)
- `.pdf` (PDFs)
- Max size: 10MB

### 2. Get Extraction Result
```
GET /api/documents/{job_id}/result

Response (200):
{
  "id": "job_id",
  "status": "completed|processing|failed",
  "filename": "test.jpg",
  "documentType": "Degree Certificate",
  "holder": {
    "name": "Arjun Mehta",
    "fatherName": "Rajesh Mehta",
    "dob": "1998-04-12"
  },
  "credential": {
    "degree": "B.Tech",
    "institution": "IIT Bombay",
    "year": "2020",
    "cgpa": "9.1"
  },
  "issuer": {
    "name": "IIT Bombay"
  },
  "confidence": {
    "name": 0.97,
    "degree": 0.95,
    ...
  },
  "rawText": "...",
  "createdAt": "2026-05-28T12:00:00",
  "updatedAt": "2026-05-28T12:00:05"
}
```

### 3. List All Documents
```
GET /api/documents

Response (200):
[
  { /* ExtractionResult objects */ },
  ...
]
```

### 4. Delete Document
```
DELETE /api/documents/{job_id}

Response: 204 No Content
```

### 5. Health Check
```
GET /health

Response (200):
{
  "status": "healthy"
}
```

## Project Structure

```
backend/
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── routers/
│   ├── __init__.py
│   └── documents.py        # API endpoint handlers
├── models/
│   ├── __init__.py
│   └── schemas.py          # Pydantic data models
├── services/
│   ├── __init__.py
│   ├── ocr_service.py      # OCR operations
│   ├── llm_service.py      # LLM-based entity extraction
│   └── job_runner.py       # Background job processing
├── storage/
│   ├── __init__.py
│   └── file_store.py       # File and result persistence
├── utils/
│   ├── __init__.py
│   └── validation.py       # Upload validation utilities
└── tests/
    ├── __init__.py
    └── test_documents.py   # Unit tests
```

## How It Works

1. **Upload** - User uploads a document (PDF or image)
2. **Validation** - Backend validates file type, extension, and size
3. **Job Creation** - Document is queued as a background job
4. **Processing** - Background worker processes:
   - Preprocessing (grayscale, thresholding, etc.)
   - OCR text extraction
   - LLM-based entity extraction
   - Result persistence
5. **Result Retrieval** - User polls `/documents/{id}/result` to get results

## Background Processing

Uses `concurrent.futures.ThreadPoolExecutor` with 3 workers for parallel document processing.

Processing pipeline:
```
1. Preprocess Image (contrast, noise reduction)
   ↓
2. Extract Text (OCR with EasyOCR/Tesseract)
   ↓
3. Extract Entities (Claude LLM)
   ↓
4. Save Results (JSON to disk)
```

## File Organization

- **Uploads**: Stored in `uploads/` with UUID-based filenames
- **Results**: Stored in `results/` as JSON files

## Troubleshooting

### "Tesseract is not installed"
This is a warning, not an error. The system falls back to EasyOCR.
To install Tesseract (optional):
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

### Upload fails with "Unsupported file type"
Ensure content-type is correct:
- JPEG: `image/jpeg`
- PNG: `image/png`
- PDF: `application/pdf`

### Job stuck in "processing"
Check the server logs for errors. Jobs are processed in serial by background workers.

## Testing

Run the comprehensive test suite:
```bash
python comprehensive_test.py
```

Or test individual endpoints:
```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/api/documents

# Upload a document
curl -X POST -F "file=@document.jpg" http://localhost:8000/api/documents/process

# Get result
curl http://localhost:8000/api/documents/{job_id}/result
```

## Performance Notes

- **Upload latency**: ~100ms (file save + validation)
- **Processing time**: ~2-5 seconds per document (depends on size)
- **Concurrent jobs**: Up to 3 documents processed in parallel
- **Storage**: All results persisted to disk (survive server restart)

## Future Enhancements

- [ ] Expand supported document types
- [ ] Improve Gemini prompt tuning and JSON parsing
- [ ] Add database backend (PostgreSQL)
- [ ] Implement WebSocket for real-time progress updates
- [ ] Add retry logic for transient failures
- [ ] Implement request rate limiting
- [ ] Add authentication and authorization
