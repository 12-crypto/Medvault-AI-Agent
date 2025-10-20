"""Common test fixtures and utilities"""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_patient_text():
    """Sample patient demographic text"""
    return """
    Patient Name: John Doe
    Date of Birth: 01/15/1980
    Sex: Male
    Address: 123 Main St
    City: Springfield
    State: IL
    Zip: 62701
    Phone: (555) 123-4567
    """


@pytest.fixture
def sample_insurance_text():
    """Sample insurance information text"""
    return """
    Insurance: Medicare
    Policy Number: 1234567890A
    Group Number: GRP123
    Subscriber: Self
    """


@pytest.fixture
def sample_clinical_notes():
    """Sample clinical notes"""
    return """
    Chief Complaint: Patient presents with chest pain and shortness of breath
    
    History: 65-year-old male with hypertension and diabetes. Onset 2 hours ago.
    
    Exam: BP 160/95, HR 92, RR 18. Chest auscultation reveals bilateral rales.
    
    Assessment:
    1. Acute congestive heart failure exacerbation
    2. Type 2 diabetes mellitus with poor control
    3. Essential hypertension
    
    Plan:
    - Admit for monitoring
    - Diuresis with IV furosemide
    - Adjust diabetes medications
    - Cardiology consult
    """
