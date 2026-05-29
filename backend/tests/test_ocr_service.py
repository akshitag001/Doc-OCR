import pytest
from services.ocr_service import OCRService
from models.exceptions import DocumentQualityError
from PIL import Image
import tempfile
import os

@pytest.fixture
def test_image_path():
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "test.png")
    img = Image.new("RGB", (200, 200), color="white")
    img.save(path)
    yield path
    os.remove(path)
    os.rmdir(tmp_dir)

def test_preprocess_creates_output_file(test_image_path):
    ocr = OCRService()
    out_path = ocr.preprocess_image(test_image_path)
    assert os.path.exists(out_path)

def test_extract_text_returns_required_keys(test_image_path, monkeypatch):
    ocr = OCRService()
    monkeypatch.setattr(
        ocr,
        "_ocr_with_easyocr",
        lambda p: ("word " * 12, [{"text": "word", "confidence": 90.0, "bbox": [0, 0, 10, 10]}], 90.0),
    )
    monkeypatch.setattr(ocr, "_ocr_with_tesseract", lambda p: ("", [], 0.0))
    out_path = ocr.preprocess_image(test_image_path)
    result = ocr.extract_text(out_path)
    for key in ["raw_text", "blocks", "page_results", "overall_confidence"]:
        assert key in result

def test_low_quality_image_raises_document_quality_error(monkeypatch):
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "black.png")
    img = Image.new("RGB", (200, 200), color="black")
    img.save(path)
    ocr = OCRService()
    monkeypatch.setattr(ocr, "_ocr_with_easyocr", lambda p: ("", [], 0.0))
    monkeypatch.setattr(ocr, "_ocr_with_tesseract", lambda p: ("", [], 0.0))
    with pytest.raises(DocumentQualityError):
        ocr.extract_text(path)
    os.remove(path)
    os.rmdir(tmp_dir)
