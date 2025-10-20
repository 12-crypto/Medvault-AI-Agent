"""
CMS-1500 Validation Rules
Implements field-level validation per NUCC and Medicare Claims Processing Manual.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .schema import CMS1500Claim, ICDIndicator, ServiceLineInfo

logger = logging.getLogger(__name__)


class ValidationMessage(BaseModel):
    """Individual validation message"""
    field: str = Field(..., description="Field name/number")
    severity: str = Field(..., description="error|warning|info")
    message: str
    rule_id: str = Field(..., description="Reference to NUCC/CMS rule")
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    """Complete validation result"""
    valid: bool
    messages: List[ValidationMessage] = Field(default_factory=list)
    warnings_count: int = 0
    errors_count: int = 0
    info_count: int = 0
    
    def add_message(self, msg: ValidationMessage):
        """Add a validation message and update counts"""
        self.messages.append(msg)
        if msg.severity == "error":
            self.errors_count += 1
            self.valid = False
        elif msg.severity == "warning":
            self.warnings_count += 1
        else:
            self.info_count += 1


class CMS1500Validator:
    """
    Validates CMS-1500 claims per NUCC and CMS specifications.
    
    References:
    - NUCC 1500 Instruction Manual
    - Medicare Claims Processing Manual Ch. 26
    - IOM Pub 100-04
    """
    
    def validate(self, claim: CMS1500Claim) -> ValidationResult:
        """
        Perform comprehensive validation of claim.
        
        Args:
            claim: CMS1500Claim object
            
        Returns:
            ValidationResult with all issues
        """
        result = ValidationResult(valid=True)
        
        # Required fields
        self._validate_required_fields(claim, result)
        
        # Item-specific validations
        self._validate_item_1a(claim, result)  # Insured ID
        self._validate_item_2_3(claim, result)  # Patient info
        self._validate_item_6(claim, result)  # Relationship
        self._validate_item_10(claim, result)  # Condition related to
        self._validate_item_11(claim, result)  # Insurance info
        self._validate_item_17(claim, result)  # Referring provider
        self._validate_item_21(claim, result)  # Diagnoses
        self._validate_item_23(claim, result)  # Prior auth
        self._validate_item_24(claim, result)  # Service lines (critical)
        self._validate_item_25(claim, result)  # Tax ID
        self._validate_item_28_29(claim, result)  # Charges
        self._validate_item_32(claim, result)  # Service facility
        self._validate_item_33(claim, result)  # Billing provider
        
        # Cross-field validations
        self._validate_diagnosis_pointers(claim, result)
        self._validate_date_logic(claim, result)
        
        return result
    
    def _validate_required_fields(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate required fields are present"""
        
        required = [
            ("1a", claim.insured_id_number, "Insured's ID Number"),
            ("2", claim.patient_last_name, "Patient Last Name"),
            ("2", claim.patient_first_name, "Patient First Name"),
            ("3", claim.patient_dob, "Patient Date of Birth"),
            ("3", claim.patient_sex, "Patient Sex"),
            ("21", claim.icd_indicator, "ICD Indicator"),
            ("33a", claim.billing_provider_npi, "Billing Provider NPI"),
        ]
        
        for field_num, value, name in required:
            if not value:
                result.add_message(ValidationMessage(
                    field=field_num,
                    severity="error",
                    message=f"{name} is required",
                    rule_id=f"NUCC-{field_num}-REQ"
                ))
    
    def _validate_item_1a(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 1a: Insured's ID Number"""
        if claim.insured_id_number:
            if len(claim.insured_id_number) > 29:
                result.add_message(ValidationMessage(
                    field="1a",
                    severity="error",
                    message="Insured's ID cannot exceed 29 characters",
                    rule_id="NUCC-1a-LEN"
                ))
    
    def _validate_item_2_3(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Items 2-3: Patient name and demographics"""
        
        # Name length checks
        if len(claim.patient_last_name) > 35:
            result.add_message(ValidationMessage(
                field="2",
                severity="error",
                message="Patient last name exceeds 35 characters",
                rule_id="NUCC-2-LEN"
            ))
        
        # DOB format check
        if claim.patient_dob:
            if not self._validate_date_format(claim.patient_dob):
                result.add_message(ValidationMessage(
                    field="3",
                    severity="error",
                    message="Patient DOB must be in MM DD YYYY format",
                    rule_id="NUCC-3-FMT",
                    suggestion="Use MM DD YYYY with spaces"
                ))
        
        # Sex validation
        if claim.patient_sex not in ['M', 'F', 'U']:
            result.add_message(ValidationMessage(
                field="3",
                severity="error",
                message="Patient sex must be M, F, or U",
                rule_id="NUCC-3-SEX"
            ))
    
    def _validate_item_6(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 6: Patient relationship to insured"""
        
        relationships = [
            claim.patient_relationship_self,
            claim.patient_relationship_spouse,
            claim.patient_relationship_child,
            claim.patient_relationship_other
        ]
        
        if not any(relationships):
            result.add_message(ValidationMessage(
                field="6",
                severity="error",
                message="Patient relationship to insured must be specified",
                rule_id="NUCC-6-REQ"
            ))
        
        if sum(relationships) > 1:
            result.add_message(ValidationMessage(
                field="6",
                severity="error",
                message="Only one relationship can be selected",
                rule_id="NUCC-6-EXCL"
            ))
    
    def _validate_item_10(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 10: Condition related to"""
        
        # If auto accident, state must be provided
        if claim.condition_related_auto_accident and not claim.auto_accident_state:
            result.add_message(ValidationMessage(
                field="10b",
                severity="error",
                message="State code required when auto accident is checked",
                rule_id="NUCC-10b-STATE"
            ))
    
    def _validate_item_11(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 11: Insured's policy group"""
        
        # If not self, Item 4 (insured name) should be filled
        if not claim.patient_relationship_self and not claim.insured_name:
            result.add_message(ValidationMessage(
                field="4",
                severity="warning",
                message="Insured's name recommended when patient is not self",
                rule_id="NUCC-4-REC"
            ))
    
    def _validate_item_17(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 17: Referring provider"""
        
        # If referring provider name present, NPI should be present
        if claim.referring_provider_name and not claim.referring_provider_npi:
            result.add_message(ValidationMessage(
                field="17b",
                severity="warning",
                message="Referring provider NPI recommended when name is provided",
                rule_id="NUCC-17b-REC"
            ))
        
        # Validate NPI format if present
        if claim.referring_provider_npi:
            if not re.match(r'^\d{10}$', claim.referring_provider_npi):
                result.add_message(ValidationMessage(
                    field="17b",
                    severity="error",
                    message="Referring provider NPI must be 10 digits",
                    rule_id="NUCC-17b-FMT"
                ))
    
    def _validate_item_21(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 21: Diagnosis codes (critical)"""
        
        # ICD indicator must be 0 for ICD-10
        if claim.icd_indicator != ICDIndicator.ICD10:
            result.add_message(ValidationMessage(
                field="21",
                severity="warning",
                message="ICD-9 is deprecated; should use ICD-10 (indicator 0)",
                rule_id="CMS-21-ICD10"
            ))
        
        # At least one diagnosis required
        diagnoses = claim.get_diagnoses_list()
        if not diagnoses:
            result.add_message(ValidationMessage(
                field="21",
                severity="error",
                message="At least one diagnosis code required",
                rule_id="NUCC-21-REQ"
            ))
        
        # Validate ICD-10 format
        for idx, dx_code in enumerate(diagnoses):
            if not self._validate_icd10_format(dx_code):
                letter = chr(65 + idx)  # A, B, C...
                result.add_message(ValidationMessage(
                    field=f"21{letter}",
                    severity="error",
                    message=f"Invalid ICD-10 format: {dx_code}",
                    rule_id="CMS-21-ICD10-FMT",
                    suggestion="ICD-10 format: Letter + 2 digits, optional decimal and more digits"
                ))
    
    def _validate_item_23(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 23: Prior authorization"""
        
        # If provided, should match format requirements
        if claim.prior_authorization_number:
            if len(claim.prior_authorization_number) > 30:
                result.add_message(ValidationMessage(
                    field="23",
                    severity="warning",
                    message="Prior authorization number exceeds typical length",
                    rule_id="NUCC-23-LEN"
                ))
    
    def _validate_item_24(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 24: Service lines (most complex)"""
        
        if not claim.service_lines:
            result.add_message(ValidationMessage(
                field="24",
                severity="error",
                message="At least one service line required",
                rule_id="NUCC-24-REQ"
            ))
            return
        
        for idx, line in enumerate(claim.service_lines, start=1):
            line_id = f"24.{idx}"
            
            # Date validation
            if not self._validate_date_format(line.date_from):
                result.add_message(ValidationMessage(
                    field=f"{line_id}A",
                    severity="error",
                    message=f"Line {idx}: Invalid date format",
                    rule_id="NUCC-24A-FMT"
                ))
            
            # Place of Service
            if not re.match(r'^\d{2}$', line.place_of_service):
                result.add_message(ValidationMessage(
                    field=f"{line_id}B",
                    severity="error",
                    message=f"Line {idx}: Place of Service must be 2 digits",
                    rule_id="NUCC-24B-FMT"
                ))
            
            # CPT/HCPCS code
            if not self._validate_cpt_hcpcs(line.cpt_hcpcs):
                result.add_message(ValidationMessage(
                    field=f"{line_id}D",
                    severity="error",
                    message=f"Line {idx}: Invalid CPT/HCPCS code format",
                    rule_id="NUCC-24D-FMT"
                ))
            
            # Diagnosis pointer
            if not line.diagnosis_pointer:
                result.add_message(ValidationMessage(
                    field=f"{line_id}E",
                    severity="error",
                    message=f"Line {idx}: Diagnosis pointer required",
                    rule_id="NUCC-24E-REQ"
                ))
            
            # Rendering provider NPI in 24J
            if line.rendering_provider_id:
                if not re.match(r'^\d{10}$', line.rendering_provider_id):
                    result.add_message(ValidationMessage(
                        field=f"{line_id}J",
                        severity="warning",
                        message=f"Line {idx}: Rendering provider ID should be 10-digit NPI",
                        rule_id="NUCC-24J-NPI"
                    ))
    
    def _validate_item_25(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 25: Federal Tax ID"""
        
        if claim.federal_tax_id:
            # Remove hyphens for validation
            tax_id = claim.federal_tax_id.replace('-', '')
            
            # EIN: 9 digits, SSN: 9 digits
            if not re.match(r'^\d{9}$', tax_id):
                result.add_message(ValidationMessage(
                    field="25",
                    severity="error",
                    message="Federal Tax ID must be 9 digits (EIN or SSN)",
                    rule_id="NUCC-25-FMT"
                ))
            
            # Checkbox validation
            if not (claim.tax_id_type_ein or claim.tax_id_type_ssn):
                result.add_message(ValidationMessage(
                    field="25",
                    severity="error",
                    message="Must specify EIN or SSN checkbox",
                    rule_id="NUCC-25-TYPE"
                ))
    
    def _validate_item_28_29(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Items 28-29: Charges and payments"""
        
        # Total charge should match sum of service lines
        calculated_total = sum(
            line.charges * line.days_or_units
            for line in claim.service_lines
        )
        
        if abs(claim.total_charge - calculated_total) > 0.01:
            result.add_message(ValidationMessage(
                field="28",
                severity="warning",
                message=f"Total charge ({claim.total_charge}) doesn't match sum of lines ({calculated_total})",
                rule_id="NUCC-28-CALC",
                suggestion=f"Should be ${calculated_total:.2f}"
            ))
    
    def _validate_item_32(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 32: Service facility"""
        
        # If facility name present, NPI required
        if claim.service_facility_name and not claim.service_facility_npi:
            result.add_message(ValidationMessage(
                field="32a",
                severity="error",
                message="Service facility NPI required when facility name provided",
                rule_id="NUCC-32a-REQ"
            ))
        
        # Validate NPI format
        if claim.service_facility_npi:
            if not re.match(r'^\d{10}$', claim.service_facility_npi):
                result.add_message(ValidationMessage(
                    field="32a",
                    severity="error",
                    message="Service facility NPI must be 10 digits",
                    rule_id="NUCC-32a-FMT"
                ))
    
    def _validate_item_33(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate Item 33: Billing provider (required)"""
        
        if not claim.billing_provider_npi:
            result.add_message(ValidationMessage(
                field="33a",
                severity="error",
                message="Billing provider NPI is required",
                rule_id="NUCC-33a-REQ"
            ))
        else:
            if not re.match(r'^\d{10}$', claim.billing_provider_npi):
                result.add_message(ValidationMessage(
                    field="33a",
                    severity="error",
                    message="Billing provider NPI must be 10 digits",
                    rule_id="NUCC-33a-FMT"
                ))
        
        # Name and address recommended
        if not claim.billing_provider_name:
            result.add_message(ValidationMessage(
                field="33",
                severity="warning",
                message="Billing provider name recommended",
                rule_id="NUCC-33-NAME"
            ))
    
    def _validate_diagnosis_pointers(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate diagnosis pointers in service lines reference valid diagnoses"""
        
        valid_letters = set()
        for letter in 'ABCDEFGHIJKL':
            if claim.get_diagnosis_by_letter(letter):
                valid_letters.add(letter)
        
        for idx, line in enumerate(claim.service_lines, start=1):
            if line.diagnosis_pointer:
                for ptr in line.diagnosis_pointer:
                    if ptr not in valid_letters:
                        result.add_message(ValidationMessage(
                            field=f"24.{idx}E",
                            severity="error",
                            message=f"Line {idx}: Diagnosis pointer '{ptr}' references empty diagnosis code",
                            rule_id="CMS-24E-REF",
                            suggestion=f"Valid pointers: {', '.join(sorted(valid_letters))}"
                        ))
    
    def _validate_date_logic(self, claim: CMS1500Claim, result: ValidationResult):
        """Validate logical consistency of dates"""
        
        # Service dates should be after patient DOB
        # Simplified check - in production would parse dates properly
        pass
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date is in MM DD YYYY format"""
        if not date_str:
            return False
        # Allow MM DD YYYY or MM/DD/YYYY or MM-DD-YYYY
        patterns = [
            r'^\d{2}\s\d{2}\s\d{4}$',
            r'^\d{2}/\d{2}/\d{4}$',
            r'^\d{2}-\d{2}-\d{4}$'
        ]
        return any(re.match(p, date_str) for p in patterns)
    
    def _validate_icd10_format(self, code: str) -> bool:
        """Validate ICD-10 code format"""
        if not code:
            return False
        # ICD-10: Letter + 2 digits, optional decimal and 1-4 more digits
        return bool(re.match(r'^[A-TV-Z]\d{2}(\.\d{1,4})?$', code))
    
    def _validate_cpt_hcpcs(self, code: str) -> bool:
        """Validate CPT/HCPCS code format"""
        if not code:
            return False
        # CPT: 5 digits, HCPCS: Letter + 4 digits
        return bool(re.match(r'^(\d{5}|[A-Z]\d{4})$', code))


def validate_claim(claim: CMS1500Claim) -> Dict[str, Any]:
    """
    Convenience function to validate a claim.
    
    Returns:
        Validation result as dictionary
    """
    validator = CMS1500Validator()
    result = validator.validate(claim)
    return result.model_dump()
