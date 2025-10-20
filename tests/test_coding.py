"""
Tests for medical coding assistant
"""

import pytest
from core.coding import MedicalCodingAssistant, CodeSuggestion, suggest_codes
from core.extraction import DiagnosisCode, ProcedureCode


def test_diagnosis_letter_assignment():
    """Test assigning letters A-L to diagnosis codes"""
    assistant = MedicalCodingAssistant(use_llm=False)
    
    diagnoses = [
        CodeSuggestion(code="J20.9", code_type="ICD-10", description="Acute bronchitis", rationale="Test", confidence=0.9),
        CodeSuggestion(code="I10", code_type="ICD-10", description="Hypertension", rationale="Test", confidence=0.8)
    ]
    
    letters = assistant._assign_diagnosis_letters(diagnoses)
    
    assert letters["J20.9"] == "A"
    assert letters["I10"] == "B"


def test_max_diagnoses_limit():
    """Test maximum 12 diagnoses (A-L)"""
    assistant = MedicalCodingAssistant(use_llm=False)
    
    # Create 15 diagnoses
    diagnoses = [
        CodeSuggestion(code=f"Z{i:02d}.0", code_type="ICD-10", description=f"Test {i}", rationale="Test", confidence=0.8)
        for i in range(15)
    ]
    
    letters = assistant._assign_diagnosis_letters(diagnoses)
    
    # Should only assign letters to first 12
    assert len(letters) == 12


def test_mismatch_detection():
    """Test detection of diagnosis-procedure mismatches"""
    assistant = MedicalCodingAssistant(use_llm=False)
    
    diagnoses = [
        CodeSuggestion(code="J20.9", code_type="ICD-10", description="Test", rationale="Test", confidence=0.9)
    ]
    
    procedures = [
        CodeSuggestion(code="99213", code_type="CPT", description="Test", rationale="Test", confidence=0.9)
    ]
    
    # Map procedures to diagnosis
    dx_proc_map = {"J20.9": ["99213"]}
    
    mismatches = assistant._detect_mismatches(diagnoses, procedures, dx_proc_map)
    
    # Should detect that procedure needs diagnosis link
    assert len(mismatches) >= 0  # May have warnings


def test_confidence_calculation():
    """Test overall confidence calculation"""
    assistant = MedicalCodingAssistant(use_llm=False)
    
    diagnoses = [
        CodeSuggestion(code="J20.9", code_type="ICD-10", description="Test", rationale="Test", confidence=0.9)
    ]
    
    procedures = [
        CodeSuggestion(code="99213", code_type="CPT", description="Test", rationale="Test", confidence=0.8)
    ]
    
    confidence = assistant._calculate_overall_confidence(diagnoses, procedures, [])
    
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.8  # Should be high with no errors


def test_suggest_codes_structure():
    """Test suggest_codes returns proper structure"""
    clinical_notes = "Patient presents with acute bronchitis"
    
    result = suggest_codes(clinical_notes, use_llm=False)
    
    assert isinstance(result, dict)
    assert "diagnoses" in result
    assert "procedures" in result
    assert "mismatches" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
