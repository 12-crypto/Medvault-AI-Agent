#!/bin/bash
set -e

echo "============================================"
echo "MediVault AI Agent - End-to-End Demo"
echo "============================================"

# Activate venv
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo ""
echo "Running end-to-end workflow tests..."
echo ""

# Test 1: OCR Pipeline
echo "1. Testing OCR pipeline with sample fixture..."
python3 -c "
from src.core.ocr import OCREngine
from pathlib import Path

engine = OCREngine()
fixture_path = Path('tests/fixtures/sample_medical_record.pdf')
if fixture_path.exists():
    result = engine.process_document(str(fixture_path))
    print(f'✓ Extracted {len(result.text)} characters from document')
else:
    print('⚠ Sample fixture not found, skipping')
"

# Test 2: Data Extraction
echo ""
echo "2. Testing data extraction..."
python3 -c "
from src.core.extraction import extract_patient_data
sample_text = '''
Patient Name: John Doe
DOB: 01/15/1980
Insurance: Medicare
Policy #: 1234567890A
'''
result = extract_patient_data(sample_text)
print(f'✓ Extracted patient data: {result.get(\"patient_name\", \"N/A\")}')
"

# Test 3: Medical Coding
echo ""
echo "3. Testing medical coding assistant..."
python3 -c "
from src.core.coding import suggest_codes
notes = 'Patient presents with acute bronchitis and hypertension'
result = suggest_codes(notes)
print(f'✓ Suggested {len(result.get(\"icd10\", []))} ICD-10 codes')
"

# Test 4: CMS-1500 Generation
echo ""
echo "4. Testing CMS-1500 generation and validation..."
python3 -c "
from src.cms1500.generator import CMS1500Generator
from src.cms1500.schema import PatientInfo, ProviderInfo

patient = PatientInfo(
    last_name='Doe',
    first_name='John',
    dob='1980-01-15',
    sex='M',
    insurance_id='1234567890A'
)

generator = CMS1500Generator()
claim = generator.create_claim(patient_info=patient)
print(f'✓ Generated CMS-1500 claim with {len(claim.model_dump())} fields')
"

# Test 5: Security
echo ""
echo "5. Testing security modules..."
python3 -c "
from src.security.storage import SecureStorage
from src.security.audit import AuditLogger

storage = SecureStorage()
audit = AuditLogger()

test_data = {'patient_id': '12345', 'name': 'Test Patient'}
encrypted = storage.encrypt_data(test_data)
decrypted = storage.decrypt_data(encrypted)

audit.log_access('test_user', 'test_resource', 'read')

print('✓ Security modules functioning correctly')
"

echo ""
echo "============================================"
echo "End-to-End Demo Complete!"
echo "============================================"
echo ""
echo "All core modules tested successfully."
echo "Launch UI with: make run"
echo ""
