import os
import shutil
import tempfile
import pytest


@pytest.fixture(autouse=True)
def temp_uploads_and_results(monkeypatch):
    base_dir = tempfile.mkdtemp()
    uploads_dir = os.path.join(base_dir, "uploads")
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    monkeypatch.setenv("UPLOADS_DIR", uploads_dir)
    monkeypatch.setenv("RESULTS_DIR", results_dir)
    yield uploads_dir, results_dir
    shutil.rmtree(base_dir)