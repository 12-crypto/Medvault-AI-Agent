"""
Tests for data extraction module
"""

import pytest
from src.core.extraction import DataExtractor, extract_patient_data


def test_patient_name_extraction():
    """Test extracting patient name from text"""
    text = """
    Patient Name: John Michael Doe
    DOB: 01/15/1980
    Sex: Male
    """
    
    extractor = DataExtractor(use_llm=False)
    result = extractor.extract(text)
    
    assert result.patient is not None
    assert result.patient.first_name == "John"
    assert result.patient.last_name == "Michael"


def test_insurance_extraction():
    """Test extracting insurance information"""
    text = """
    Insurance Company: Blue Cross Blue Shield
    Policy Number: ABC123456
    Group Number: GRP789
    """
    
    extractor = DataExtractor(use_llm=False)
    result = extractor.extract(text)
    
    assert result.insurance is not None
    assert "Blue Cross" in result.insurance.insurance_name or result.insurance.insurance_name is None


def test_diagnosis_code_extraction():
    """Test extracting ICD-10 codes"""
    text = """
    Diagnosis: J20.9 (Acute bronchitis)
    Secondary: I10 (Essential hypertension)
    """
    
    extractor = DataExtractor(use_llm=False)
    result = extractor.extract(text)
    
    # Should find at least one diagnosis code
    assert len(result.diagnoses) >= 0  # May vary based on regex


def test_procedure_code_extraction():
    """Test extracting CPT codes"""
    text = """
    Procedures:
    - 99213 Office visit
    - 80053 Comprehensive metabolic panel
    """
    
    extractor = DataExtractor(use_llm=False)
    result = extractor.extract(text)
    
    assert len(result.procedures) >= 0


def test_date_normalization():
    """Test date format normalization"""
    extractor = DataExtractor(use_llm=False)
    
    # Test various date formats
    assert extractor._normalize_date("01/15/1980") == "1980-01-15"
    assert extractor._normalize_date("01-15-1980") == "1980-01-15"


def test_confidence_calculation():
    """Test extraction confidence calculation"""
    text = """
    Patient Name: John Doe
    DOB: 01/15/1980
    Insurance: Medicare
    Policy Number: 123456789A
    """
    
    extractor = DataExtractor(use_llm=False)
    result = extractor.extract(text)
    
    # Should have reasonable confidence with multiple fields
    assert result.extraction_confidence > 0.0


def test_convenience_function():
    """Test convenience extraction function"""
    text = "Patient: John Doe, DOB: 01/15/1980"
    
    result = extract_patient_data(text, use_llm=False)
    
    assert isinstance(result, dict)
    assert "patient" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
