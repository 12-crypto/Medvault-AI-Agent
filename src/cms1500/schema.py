"""
CMS-1500 Claim Form Schema (Version 02/12)
Comprehensive typed model for all 33 numbered items per NUCC specifications.

References:
- NUCC 1500 Instruction Manual
- Medicare Claims Processing Manual Chapter 26
- CMS Internet-Only Manual (IOM) 100-04
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ICDIndicator(str, Enum):
    """Item 21: ICD Indicator"""
    ICD10 = "0"  # ICD-10-CM
    ICD9 = "9"   # ICD-9-CM (legacy)


class ServiceLineInfo(BaseModel):
    """Item 24: Service line information (up to 6 lines)"""
    # 24A: Date of Service
    date_from: str = Field(..., description="MM DD YY format")
    date_to: Optional[str] = Field(None, description="MM DD YY format")
    
    # 24B: Place of Service
    place_of_service: str = Field(..., max_length=2, description="2-digit POS code")
    
    # 24C: EMG (Emergency indicator)
    emg: Optional[str] = Field(None, max_length=1)
    
    # 24D: Procedures, Services, or Supplies (CPT/HCPCS)
    cpt_hcpcs: str = Field(..., description="CPT/HCPCS code")
    modifier1: Optional[str] = Field(None, max_length=2)
    modifier2: Optional[str] = Field(None, max_length=2)
    modifier3: Optional[str] = Field(None, max_length=2)
    modifier4: Optional[str] = Field(None, max_length=2)
    
    # 24E: Diagnosis Pointer (letters A-L)
    diagnosis_pointer: str = Field(..., description="1-4 letters from A-L, e.g., 'A' or 'ABC'")
    
    # 24F: Charges
    charges: float = Field(..., ge=0, description="Dollar amount")
    
    # 24G: Days or Units
    days_or_units: int = Field(default=1, ge=1)
    
    # 24H: EPSDT Family Plan
    epsdt_family_plan: Optional[str] = None
    
    # 24I: ID Qualifier
    id_qualifier: Optional[str] = Field(None, max_length=2)
    
    # 24J: Rendering Provider ID
    rendering_provider_id: Optional[str] = Field(None, description="NPI or other ID")
    
    @validator('diagnosis_pointer')
    def validate_diagnosis_pointer(cls, v):
        """Validate diagnosis pointer contains only A-L"""
        if v:
            for char in v:
                if char not in 'ABCDEFGHIJKL':
                    raise ValueError(f"Invalid diagnosis pointer: {char}. Must be A-L.")
        return v


class CMS1500Claim(BaseModel):
    """
    Complete CMS-1500 (02/12) claim form.
    
    Based on NUCC specifications with 33 numbered items plus carrier information.
    """
    
    # CARRIER/PAYER INFORMATION (Top section)
    carrier_name: Optional[str] = None
    carrier_address: Optional[str] = None
    carrier_city_state_zip: Optional[str] = None
    
    # 1: Type of Insurance
    insurance_type_medicare: bool = False
    insurance_type_medicaid: bool = False
    insurance_type_tricare: bool = False
    insurance_type_champva: bool = False
    insurance_type_group_health: bool = False
    insurance_type_feca: bool = False
    insurance_type_other: bool = False
    
    # 1a: Insured's ID Number
    insured_id_number: str = Field(..., description="Required")
    
    # 2: Patient's Name (Last, First, Middle Initial)
    patient_last_name: str = Field(..., description="Required")
    patient_first_name: str = Field(..., description="Required")
    patient_middle_initial: Optional[str] = Field(None, max_length=1)
    
    # 3: Patient's Birth Date and Sex
    patient_dob: str = Field(..., description="MM DD YYYY")
    patient_sex: str = Field(..., pattern="^[MFU]$", description="M/F/U")
    
    # 4: Insured's Name
    insured_name: Optional[str] = None
    
    # 5: Patient's Address
    patient_address: Optional[str] = None
    patient_city: Optional[str] = None
    patient_state: Optional[str] = Field(None, max_length=2)
    patient_zip: Optional[str] = None
    patient_phone: Optional[str] = None
    
    # 6: Patient Relationship to Insured
    patient_relationship_self: bool = False
    patient_relationship_spouse: bool = False
    patient_relationship_child: bool = False
    patient_relationship_other: bool = False
    
    # 7: Insured's Address
    insured_address: Optional[str] = None
    insured_city: Optional[str] = None
    insured_state: Optional[str] = Field(None, max_length=2)
    insured_zip: Optional[str] = None
    insured_phone: Optional[str] = None
    
    # 8: Reserved for NUCC Use
    patient_status_single: bool = False
    patient_status_married: bool = False
    patient_status_other: bool = False
    patient_status_employed: bool = False
    patient_status_full_time_student: bool = False
    patient_status_part_time_student: bool = False
    
    # 9: Other Insured's Name
    other_insured_name: Optional[str] = None
    # 9a: Other Insured's Policy or Group Number
    other_insured_policy: Optional[str] = None
    # 9b: Reserved for NUCC Use (DOB, Sex)
    other_insured_dob: Optional[str] = None
    other_insured_sex: Optional[str] = Field(None, pattern="^[MFU]$")
    # 9c: Reserved for NUCC Use (Employer/School)
    other_insured_employer: Optional[str] = None
    # 9d: Insurance Plan Name or Program Name
    other_insurance_plan_name: Optional[str] = None
    
    # 10: Is Patient's Condition Related To:
    # 10a: Employment
    condition_related_employment: Optional[bool] = None
    # 10b: Auto Accident
    condition_related_auto_accident: Optional[bool] = None
    auto_accident_state: Optional[str] = Field(None, max_length=2)
    # 10c: Other Accident
    condition_related_other_accident: Optional[bool] = None
    # 10d: Claim Codes (Designated by NUCC)
    claim_codes: Optional[str] = None
    
    # 11: Insured's Policy Group or FECA Number
    insured_policy_group: Optional[str] = None
    # 11a: Insured's Date of Birth, Sex
    insured_dob: Optional[str] = None
    insured_sex: Optional[str] = Field(None, pattern="^[MFU]$")
    # 11b: Other Claim ID (Designated by NUCC)
    other_claim_id: Optional[str] = None
    # 11c: Insurance Plan Name or Program Name
    insurance_plan_name: Optional[str] = None
    # 11d: Is There Another Health Benefit Plan?
    another_health_benefit_plan: Optional[bool] = None
    
    # 12: Patient's or Authorized Person's Signature
    patient_signature: Optional[str] = Field(default="Signature on File")
    patient_signature_date: Optional[str] = None
    
    # 13: Insured's or Authorized Person's Signature
    insured_signature: Optional[str] = Field(default="Signature on File")
    
    # 14: Date of Current Illness, Injury, or Pregnancy (LMP)
    date_of_current_illness: Optional[str] = None
    illness_qualifier: Optional[str] = Field(None, description="431=Onset, 484=Last Menstrual Period")
    
    # 15: Other Date
    other_date: Optional[str] = None
    other_date_qualifier: Optional[str] = None
    
    # 16: Dates Patient Unable to Work
    unable_to_work_from: Optional[str] = None
    unable_to_work_to: Optional[str] = None
    
    # 17: Name of Referring Provider or Other Source
    referring_provider_name: Optional[str] = None
    # 17a: ID Number of Referring Provider (legacy)
    referring_provider_other_id: Optional[str] = None
    # 17b: NPI of Referring Provider
    referring_provider_npi: Optional[str] = Field(None, pattern="^\\d{10}$")
    
    # 18: Hospitalization Dates Related to Current Services
    hospitalization_from: Optional[str] = None
    hospitalization_to: Optional[str] = None
    
    # 19: Additional Claim Information (Designated by NUCC)
    additional_claim_info: Optional[str] = Field(None, max_length=80)
    
    # 20: Outside Lab? $ Charges
    outside_lab: Optional[bool] = None
    outside_lab_charges: Optional[float] = Field(None, ge=0)
    
    # 21: Diagnosis or Nature of Illness or Injury
    icd_indicator: ICDIndicator = Field(..., description="0=ICD-10-CM, 9=ICD-9-CM")
    diagnosis_a: Optional[str] = None
    diagnosis_b: Optional[str] = None
    diagnosis_c: Optional[str] = None
    diagnosis_d: Optional[str] = None
    diagnosis_e: Optional[str] = None
    diagnosis_f: Optional[str] = None
    diagnosis_g: Optional[str] = None
    diagnosis_h: Optional[str] = None
    diagnosis_i: Optional[str] = None
    diagnosis_j: Optional[str] = None
    diagnosis_k: Optional[str] = None
    diagnosis_l: Optional[str] = None
    
    # 22: Resubmission Code and Original Ref. No.
    resubmission_code: Optional[str] = None
    original_ref_no: Optional[str] = None
    
    # 23: Prior Authorization Number
    prior_authorization_number: Optional[str] = None
    
    # 24: Service Lines (up to 6)
    service_lines: List[ServiceLineInfo] = Field(default_factory=list, max_items=6)
    
    # 25: Federal Tax ID Number
    federal_tax_id: Optional[str] = Field(None, description="EIN or SSN")
    tax_id_type_ssn: bool = False
    tax_id_type_ein: bool = False
    
    # 26: Patient's Account No.
    patient_account_number: Optional[str] = Field(None, max_length=15)
    
    # 27: Accept Assignment?
    accept_assignment: Optional[bool] = None
    
    # 28: Total Charge
    total_charge: float = Field(default=0.0, ge=0)
    
    # 29: Amount Paid
    amount_paid: Optional[float] = Field(None, ge=0)
    
    # 30: Reserved for NUCC Use (Balance Due)
    balance_due: Optional[float] = Field(None, ge=0)
    
    # 31: Signature of Physician or Supplier
    physician_signature: Optional[str] = Field(default="Signature on File")
    physician_signature_date: Optional[str] = None
    
    # 32: Service Facility Location Information
    service_facility_name: Optional[str] = None
    service_facility_address: Optional[str] = None
    service_facility_city: Optional[str] = None
    service_facility_state: Optional[str] = Field(None, max_length=2)
    service_facility_zip: Optional[str] = None
    # 32a: NPI
    service_facility_npi: Optional[str] = Field(None, pattern="^\\d{10}$")
    # 32b: Other ID
    service_facility_other_id: Optional[str] = None
    
    # 33: Billing Provider Info & Ph #
    billing_provider_name: Optional[str] = None
    billing_provider_address: Optional[str] = None
    billing_provider_city: Optional[str] = None
    billing_provider_state: Optional[str] = Field(None, max_length=2)
    billing_provider_zip: Optional[str] = None
    billing_provider_phone: Optional[str] = None
    # 33a: NPI
    billing_provider_npi: Optional[str] = Field(None, pattern="^\\d{10}$")
    # 33b: Other ID
    billing_provider_other_id: Optional[str] = None
    
    # Metadata
    form_version: str = Field(default="02/12", description="CMS-1500 version")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('service_lines')
    def validate_service_lines(cls, v):
        """Ensure at least one service line and max 6"""
        if not v:
            raise ValueError("At least one service line required")
        if len(v) > 6:
            raise ValueError("Maximum 6 service lines allowed")
        return v
    
    @validator('total_charge')
    def calculate_total_charge(cls, v, values):
        """Calculate total charge from service lines"""
        service_lines = values.get('service_lines', [])
        if service_lines:
            calculated = sum(line.charges * line.days_or_units for line in service_lines)
            # Allow manual override but warn if different
            if v > 0 and abs(v - calculated) > 0.01:
                import logging
                logging.warning(f"Manual total_charge ({v}) differs from calculated ({calculated})")
            return v if v > 0 else calculated
        return v
    
    def get_diagnoses_list(self) -> List[str]:
        """Get list of all diagnosis codes (A-L)"""
        diagnoses = []
        for letter in 'ABCDEFGHIJKL':
            code = getattr(self, f'diagnosis_{letter.lower()}', None)
            if code:
                diagnoses.append(code)
        return diagnoses
    
    def get_diagnosis_by_letter(self, letter: str) -> Optional[str]:
        """Get diagnosis code by letter (A-L)"""
        if letter not in 'ABCDEFGHIJKL':
            return None
        return getattr(self, f'diagnosis_{letter.lower()}', None)
