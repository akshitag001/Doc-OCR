import requests
import time
import json

# Create a new test image
from PIL import Image
img = Image.new('RGB', (200, 200), color='white')
img.save('test_doc2.jpg', 'JPEG')

# Test upload
with open('test_doc2.jpg', 'rb') as f:
    files = {'file': ('test_doc2.jpg', f, 'image/jpeg')}
    resp = requests.post('http://localhost:8000/api/documents/process', files=files)
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}"
    job_id = resp.json()['job_id']
    print(f'✓ Upload successful: {job_id}')

# Wait for processing
time.sleep(2)

# Check result
resp = requests.get(f'http://localhost:8000/api/documents/{job_id}/result')
assert resp.status_code == 200
result = resp.json()
assert result['status'] == 'completed'
assert result['holder']['name'] == 'Arjun Mehta'
print(f'✓ Result retrieval successful')

# List documents
resp = requests.get('http://localhost:8000/api/documents')
assert resp.status_code == 200
assert len(resp.json()) > 0
print(f'✓ Document listing successful: {len(resp.json())} documents')

# Check health
resp = requests.get('http://localhost:8000/health')
assert resp.status_code == 200
print(f'✓ Health check successful')

print('\n✅ All tests passed!')
