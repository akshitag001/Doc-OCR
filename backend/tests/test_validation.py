import io
import pytest
from utils.validation import validate_upload, sanitize_filename
from fastapi import UploadFile, HTTPException

class DummyUpload:
    def __init__(self, filename, content_type, size):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(b'x' * size)
        self.file.seek(0)
        self.spool_max_size = size
        self.headers = {}

    async def read(self):
        return self.file.read()

    async def seek(self, offset: int):
        return self.file.seek(offset)

@pytest.mark.asyncio
async def test_valid_jpeg_passes():
    file = DummyUpload("test.jpg", "image/jpeg", 1024)
    await validate_upload(file)

@pytest.mark.asyncio
async def test_valid_pdf_passes():
    file = DummyUpload("test.pdf", "application/pdf", 1024)
    await validate_upload(file)

@pytest.mark.asyncio
async def test_invalid_txt_fails():
    file = DummyUpload("test.txt", "text/plain", 1024)
    with pytest.raises(HTTPException):
        await validate_upload(file)

@pytest.mark.asyncio
async def test_empty_file_fails():
    file = DummyUpload("empty.jpg", "image/jpeg", 0)
    with pytest.raises(HTTPException):
        await validate_upload(file)

@pytest.mark.asyncio
async def test_oversized_file_fails():
    file = DummyUpload("big.jpg", "image/jpeg", 11 * 1024 * 1024)
    with pytest.raises(HTTPException):
        await validate_upload(file)

def test_sanitize_filename_removes_path_traversal():
    assert sanitize_filename("../../../etc/passwd.jpg") == "etc_passwd.jpg"
