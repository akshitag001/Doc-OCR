import requests

# Test the specific job ID
job_id = '262ce9f7-9125-47f7-bd7f-7fa35e76c471'
resp = requests.get(f'http://localhost:8000/api/documents/{job_id}/result')
print(f'Backend direct - Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'  Name: {data.get("holder", {}).get("name")}')
else:
    print(f'  Error: {resp.text}')

# Also test through the frontend proxy
print()
resp2 = requests.get(f'http://localhost:3000/api/documents/{job_id}/result')
print(f'Frontend proxy - Status: {resp2.status_code}')
if resp2.status_code == 200:
    data2 = resp2.json()
    print(f'  Status: {data2.get("status")}')
    print(f'  Name: {data2.get("holder", {}).get("name")}')
else:
    print(f'  Error: {resp2.text[:200]}')
