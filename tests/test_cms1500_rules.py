"""
Tests for CMS-1500 validation rules
"""

import pytest
from datetime import datetime
from src.cms1500.schema import CMS1500Claim, ServiceLineInfo, ICDIndicator
from src.cms1500.rules import CMS1500Validator, validate_claim


@pytest.fixture
def valid_claim():
    """Create a valid CMS-1500 claim for testing"""
    claim = CMS1500Claim(
        insured_id_number="1234567890A",
        patient_last_name="Doe",
        patient_first_name="John",
        patient_dob="01 15 1980",
        patient_sex="M",
        patient_relationship_self=True,
        icd_indicator=ICDIndicator.ICD10,
        diagnosis_a="J20.9",
        diagnosis_b="I10",
        service_lines=[
            ServiceLineInfo(
                date_from="01 15 2024",
                place_of_service="11",
                cpt_hcpcs="99213",
                diagnosis_pointer="AB",
                charges=150.00,
                days_or_units=1
            )
        ],
        federal_tax_id="123456789",
        tax_id_type_ein=True,
        billing_provider_npi="1234567890",
        total_charge=150.00
    )
    return claim


def test_valid_claim(valid_claim):
    """Test that a valid claim passes validation"""
    validator = CMS1500Validator()
    result = validator.validate(valid_claim)
    
    assert result.errors_count == 0


def test_missing_required_fields():
    """Test validation fails when required fields missing"""
    claim = CMS1500Claim(
        insured_id_number="123",
        patient_last_name="Doe",
        patient_first_name="John",
        patient_dob="01 15 1980",
        patient_sex="M",
        icd_indicator=ICDIndicator.ICD10,
        service_lines=[
            ServiceLineInfo(
                date_from="01 15 2024",
                place_of_service="11",
                cpt_hcpcs="99213",
                diagnosis_pointer="A",
                charges=100.00
            )
        ]
        # Missing billing_provider_npi (required)
    )
    
    validator = CMS1500Validator()
    result = validator.validate(claim)
    
    assert result.errors_count > 0
    assert any("NPI" in msg.message for msg in result.messages if msg.severity == "error")


def test_invalid_diagnosis_code_format():
    """Test ICD-10 code format validation"""
    claim = CMS1500Claim(
        insured_id_number="123",
        patient_last_name="Doe",
        patient_first_name="John",
        patient_dob="01 15 1980",
        patient_sex="M",
        icd_indicator=ICDIndicator.ICD10,
        diagnosis_a="INVALID",  # Invalid format
        service_lines=[
            ServiceLineInfo(
                date_from="01 15 2024",
                place_of_service="11",
                cpt_hcpcs="99213",
                diagnosis_pointer="A",
                charges=100.00
            )
        ],
        billing_provider_npi="1234567890"
    )
    
    validator = CMS1500Validator()
    result = validator.validate(claim)
    
    assert any("ICD-10" in msg.message for msg in result.messages)


def test_diagnosis_pointer_validation(valid_claim):
    """Test diagnosis pointer references valid diagnosis"""
    # Add service line with invalid pointer
    valid_claim.service_lines.append(
        ServiceLineInfo(
            date_from="01 15 2024",
            place_of_service="11",
            cpt_hcpcs="99214",
            diagnosis_pointer="Z",  # Invalid - no diagnosis Z
            charges=100.00
        )
    )
    
    validator = CMS1500Validator()
    result = validator.validate(valid_claim)
    
    assert any("pointer" in msg.message.lower() for msg in result.messages)


def test_npi_format_validation():
    """Test NPI must be 10 digits"""
    claim = CMS1500Claim(
        insured_id_number="123",
        patient_last_name="Doe",
        patient_first_name="John",
        patient_dob="01 15 1980",
        patient_sex="M",
        icd_indicator=ICDIndicator.ICD10,
        diagnosis_a="J20.9",
        service_lines=[
            ServiceLineInfo(
                date_from="01 15 2024",
                place_of_service="11",
                cpt_hcpcs="99213",
                diagnosis_pointer="A",
                charges=100.00
            )
        ],
        billing_provider_npi="123"  # Too short
    )
    
    validator = CMS1500Validator()
    result = validator.validate(claim)
    
    assert result.errors_count > 0


def test_total_charge_calculation(valid_claim):
    """Test total charge matches service line sum"""
    valid_claim.total_charge = 999.99  # Wrong amount
    
    validator = CMS1500Validator()
    result = validator.validate(valid_claim)
    
    assert any("total charge" in msg.message.lower() for msg in result.messages)


def test_convenience_function(valid_claim):
    """Test convenience validation function"""
    result_dict = validate_claim(valid_claim)
    
    assert isinstance(result_dict, dict)
    assert "valid" in result_dict
    assert "messages" in result_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
