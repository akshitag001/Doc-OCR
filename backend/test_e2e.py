"""End-to-end test of OCR integration with backend API."""
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_test_document():
    """Create a test document with readable text."""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    text = """DEGREE CERTIFICATE

Name: Arjun Mehta
Father's Name: Rajesh Mehta  
Date of Birth: 12-04-1998

This certifies that
Arjun Mehta has successfully completed
Bachelor of Technology
in Computer Science Engineering

From: Indian Institute of Technology Bombay
Year of Graduation: 2020
CGPA: 9.1/10.0

Issued by:
Indian Institute of Technology Bombay
Date: 15-05-2020
"""
    
    draw.text((30, 30), text, fill='black', font=font)
    img.save('test_e2e_doc.jpg')
    print("✓ Created test document: test_e2e_doc.jpg")

def test_full_pipeline():
    """Test the complete pipeline end-to-end."""
    
    print("\n" + "="*70)
    print("END-TO-END OCR PIPELINE TEST")
    print("="*70)
    
    create_test_document()
    
    # Upload document
    print("\n[STEP 1] Uploading document...")
    with open('test_e2e_doc.jpg', 'rb') as f:
        files = {'file': ('test_e2e_doc.jpg', f, 'image/jpeg')}
        resp = requests.post('http://localhost:8000/api/documents/process', files=files)
    
    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}"
    job_id = resp.json()['job_id']
    print(f"✓ Document uploaded, job_id: {job_id}")
    
    # Wait for processing
    print("\n[STEP 2] Waiting for OCR processing...")
    time.sleep(3)
    
    # Get result
    print("\n[STEP 3] Retrieving results...")
    resp = requests.get(f'http://localhost:8000/api/documents/{job_id}/result')
    
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    result = resp.json()
    
    print(f"✓ Result retrieved")
    print(f"  Status: {result['status']}")
    print(f"  Filename: {result['filename']}")
    print(f"  Document Type: {result['documentType']}")
    
    # Verify OCR data
    print("\n[STEP 4] Verifying OCR results...")
    
    raw_text = result.get('rawText', '')
    print(f"✓ Extracted text: {len(raw_text)} characters, {len(raw_text.split())} words")
    
    if 'Arjun' in raw_text or 'Mehta' in raw_text or 'Technology' in raw_text:
        print(f"✓ Content validation: PASS (found key terms)")
    else:
        print(f"⚠ Content validation: FAIL (key terms not found)")
        print(f"  Extracted: {raw_text[:200]}...")
    
    # Verify structured extraction
    print("\n[STEP 5] Verifying structured extraction...")
    
    holder = result.get('holder', {})
    credential = result.get('credential', {})
    issuer = result.get('issuer', {})
    confidence = result.get('confidence', {})
    
    print(f"  Holder: {holder}")
    print(f"  Credential: {credential}")
    print(f"  Issuer: {issuer}")
    
    if holder.get('name'):
        print(f"✓ Extracted holder name: {holder['name']}")
    if credential.get('degree'):
        print(f"✓ Extracted degree: {credential['degree']}")
    
    # Show confidence scores
    print("\n[STEP 6] Confidence scores...")
    for key, score in sorted(confidence.items())[:5]:
        print(f"  {key}: {score:.1f}%")
    
    # Cleanup
    print("\n[CLEANUP]")
    if Path('test_e2e_doc.jpg').exists():
        Path('test_e2e_doc.jpg').unlink()
        print("✓ Removed test document")
    
    print("\n" + "="*70)
    print("✅ END-TO-END TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_full_pipeline()
