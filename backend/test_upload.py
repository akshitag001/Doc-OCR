from PIL import Image
import requests

# Create test image
img = Image.new('RGB', (100, 100), color='white')
img.save('test_doc.jpg', 'JPEG')
print('Created test_doc.jpg')

# Upload it
with open('test_doc.jpg', 'rb') as f:
    files = {'file': ('test_doc.jpg', f, 'image/jpeg')}
    resp = requests.post('http://localhost:8000/api/documents/process', files=files)
    print(f'Status: {resp.status_code}')
    result = resp.json()
    print(f'Response: {result}')
    
    if resp.status_code == 202:
        job_id = result['job_id']
        print(f'\nJob ID: {job_id}')
        print('Checking result after 3 seconds...')
        import time
        time.sleep(3)
        result_resp = requests.get(f'http://localhost:8000/api/documents/{job_id}/result')
        print(f'Result Status: {result_resp.status_code}')
        if result_resp.status_code == 200:
            print(f'Result: {result_resp.json()}')
