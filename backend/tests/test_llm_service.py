import pytest
from services.llm_service import LLMService, RateLimitError


class MockGeminiClient:
    def __init__(self, fail_times: int = 0):
        self.calls = 0
        self.fail_times = fail_times

    def generate_content(self, prompt):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RateLimitError("rate limit")
        class Response:
            text = '{"holder": {"name": "Test User"}, "credential": {"degree": "B.Tech"}, "issuer": {"name": "Test Inst"}, "confidence": {"name": 1.0}, "documentType": "DEGREE_CERTIFICATE"}'
        return Response()


@pytest.fixture
def llm():
    service = LLMService()
    service.gemini_client = MockGeminiClient()
    return service


def test_extract_entities_returns_required_structure(llm):
    result = llm.extract_entities("Test OCR text", "test.jpg")
    for key in ["holder", "credential", "issuer", "confidence", "documentType"]:
        assert key in result


def test_detect_document_type_returns_valid_label(llm):
    label = llm.detect_document_type("Degree certificate from IIT")
    assert label in ["DEGREE_CERTIFICATE", "MARKSHEET", "AADHAAR", "PASSPORT", "DRIVING_LICENSE", "UNKNOWN"]


def test_repair_json_handles_truncated_json(llm):
    broken = '{"holder": {"name": "Test User"}'
    repaired = llm.repair_json(broken)
    assert repaired == {}


def test_retry_on_rate_limit():
    service = LLMService()
    client = MockGeminiClient(fail_times=2)
    service.gemini_client = client
    result = service.extract_entities("Test OCR text", "test.jpg")
    assert client.calls == 3
    assert "holder" in result
