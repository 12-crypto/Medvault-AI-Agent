"""
Data Extraction Module
Extracts structured patient, provider, insurance, diagnosis, and procedure data
from unstructured clinical documents using LLM and rule-based approaches.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


# Data Models for Extracted Information

class PatientInfo(BaseModel):
    """Patient demographic information"""
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None  # YYYY-MM-DD format
    sex: Optional[str] = None  # M/F/U
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    marital_status: Optional[str] = None
    employment_status: Optional[str] = None
    
    @validator('sex')
    def validate_sex(cls, v):
        if v and v.upper() not in ['M', 'F', 'U']:
            return 'U'
        return v.upper() if v else None


class InsuranceInfo(BaseModel):
    """Insurance coverage information"""
    insurance_name: Optional[str] = None
    plan_name: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    subscriber_name: Optional[str] = None
    subscriber_relationship: Optional[str] = None  # Self, Spouse, Child, Other
    subscriber_dob: Optional[str] = None
    insurance_address: Optional[str] = None
    insurance_city: Optional[str] = None
    insurance_state: Optional[str] = None
    insurance_zip: Optional[str] = None
    payer_id: Optional[str] = None


class ProviderInfo(BaseModel):
    """Provider and facility information"""
    provider_name: Optional[str] = None
    provider_npi: Optional[str] = None
    facility_name: Optional[str] = None
    facility_npi: Optional[str] = None
    facility_address: Optional[str] = None
    facility_city: Optional[str] = None
    facility_state: Optional[str] = None
    facility_zip: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    taxonomy_code: Optional[str] = None


class DiagnosisCode(BaseModel):
    """Diagnosis code (ICD-10)"""
    code: str
    description: Optional[str] = None
    letter: Optional[str] = None  # A-L for CMS-1500 mapping
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_span: Optional[str] = None  # Text that led to this diagnosis


class ProcedureCode(BaseModel):
    """Procedure code (CPT/HCPCS)"""
    code: str
    description: Optional[str] = None
    modifier: Optional[str] = None
    units: int = 1
    charge: Optional[float] = None
    diagnosis_pointers: List[str] = Field(default_factory=list)  # Letters A-L
    date_of_service: Optional[str] = None
    place_of_service: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ExtractedData(BaseModel):
    """Complete extracted data from document"""
    patient: Optional[PatientInfo] = None
    insurance: Optional[InsuranceInfo] = None
    provider: Optional[ProviderInfo] = None
    diagnoses: List[DiagnosisCode] = Field(default_factory=list)
    procedures: List[ProcedureCode] = Field(default_factory=list)
    dates: Dict[str, str] = Field(default_factory=dict)  # service_date, accident_date, etc.
    amounts: Dict[str, float] = Field(default_factory=dict)  # total_charge, amount_paid, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class DataExtractor:
    """
    Extract structured data from unstructured clinical documents.
    
    Uses combination of:
    1. Rule-based regex patterns for structured fields
    2. LLM for unstructured clinical notes
    3. Entity recognition for names, dates, codes
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize extractor.
        
        Args:
            use_llm: Use LLM for enhanced extraction
        """
        self.use_llm = use_llm
        
    def extract(self, text: str, use_llm_enhancement: bool = None) -> ExtractedData:
        """
        Extract structured data from text.
        
        Args:
            text: Source text (from parsed document)
            use_llm_enhancement: Override LLM usage for this extraction
            
        Returns:
            ExtractedData object
        """
        if use_llm_enhancement is None:
            use_llm_enhancement = self.use_llm
        
        logger.info("Starting data extraction")
        
        # Extract with rule-based patterns first
        patient = self._extract_patient_info(text)
        insurance = self._extract_insurance_info(text)
        provider = self._extract_provider_info(text)
        dates = self._extract_dates(text)
        amounts = self._extract_amounts(text)
        
        # Extract codes (basic patterns, enhanced by LLM later)
        diagnoses = self._extract_diagnosis_codes(text)
        procedures = self._extract_procedure_codes(text)
        
        # Enhance with LLM if enabled
        if use_llm_enhancement:
            try:
                llm_result = self._llm_extract(text)
                
                # Merge LLM results with rule-based (LLM takes priority for missing fields)
                patient = self._merge_patient_info(patient, llm_result.get("patient"))
                insurance = self._merge_insurance_info(insurance, llm_result.get("insurance"))
                provider = self._merge_provider_info(provider, llm_result.get("provider"))
                
                # LLM may find additional codes
                if llm_result.get("diagnoses"):
                    diagnoses.extend(llm_result["diagnoses"])
                # Only extend procedures from the LLM if no procedures were extracted by rules
                # This prevents LLM-added procedure codes from appearing when the document
                # already contains explicit procedure lines.
                if llm_result.get("procedures") and not procedures:
                    procedures.extend(llm_result["procedures"])
                
            except Exception as e:
                logger.warning(f"LLM extraction failed, using rule-based only: {e}")
         
        # Calculate overall confidence
        confidence = self._calculate_confidence(patient, insurance, provider, diagnoses, procedures)
        
        return ExtractedData(
            patient=patient,
            insurance=insurance,
            provider=provider,
            diagnoses=diagnoses,
            procedures=procedures,
            dates=dates,
            amounts=amounts,
            extraction_confidence=confidence,
            metadata={"method": "hybrid" if use_llm_enhancement else "rules"}
        )
    
    def _extract_patient_info(self, text: str) -> PatientInfo:
        """Extract patient information using regex patterns"""
        
        info = PatientInfo()
        
        # Name patterns
        name_match = re.search(
            r'patient\s+name[:\s]+([A-Za-z]+)[\s,]+([A-Za-z]+)(?:[\s,]+([A-Za-z]+))?',
            text,
            re.IGNORECASE
        )
        if name_match:
            info.first_name = name_match.group(1)
            info.last_name = name_match.group(2)
            if name_match.group(3):
                info.middle_name = name_match.group(3)
        
        # DOB patterns
        dob_match = re.search(
            r'(?:dob|date\s+of\s+birth|birth\s+date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            text,
            re.IGNORECASE
        )
        if dob_match:
            info.dob = self._normalize_date(dob_match.group(1))
        
        # Sex/Gender
        sex_match = re.search(r'(?:sex|gender)[:\s]+(M|F|Male|Female)', text, re.IGNORECASE)
        if sex_match:
            sex_value = sex_match.group(1).upper()
            info.sex = 'M' if sex_value.startswith('M') else 'F'
        
        # Phone
        phone_match = re.search(r'(?:phone|tel|telephone)[:\s]+(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text, re.IGNORECASE)
        if phone_match:
            info.phone = phone_match.group(1)
        
        # Address (basic pattern)
        address_match = re.search(r'(?:address)[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
        if address_match:
            info.address = address_match.group(1).strip()
        
        return info
    
    def _extract_insurance_info(self, text: str) -> InsuranceInfo:
        """Extract insurance information"""
        
        info = InsuranceInfo()
        
        # Insurance name
        ins_name_match = re.search(
            r'insurance\s+(?:company|name|carrier)[:\s]+(.+?)(?:\n|policy)',
            text,
            re.IGNORECASE
        )
        if ins_name_match:
            info.insurance_name = ins_name_match.group(1).strip()
        
        # Policy number
        policy_match = re.search(
            r'policy\s+(?:number|#|no)[:\s]+([A-Z0-9]+)',
            text,
            re.IGNORECASE
        )
        if policy_match:
            info.policy_number = policy_match.group(1)
        
        # Group number
        group_match = re.search(
            r'group\s+(?:number|#|no)[:\s]+([A-Z0-9]+)',
            text,
            re.IGNORECASE
        )
        if group_match:
            info.group_number = group_match.group(1)
        
        # Subscriber relationship
        rel_match = re.search(
            r'relationship\s+to\s+(?:insured|subscriber)[:\s]+(Self|Spouse|Child|Other)',
            text,
            re.IGNORECASE
        )
        if rel_match:
            info.subscriber_relationship = rel_match.group(1).capitalize()
        
        return info
    
    def _extract_provider_info(self, text: str) -> ProviderInfo:
        """Extract provider/facility information"""
        
        info = ProviderInfo()
        
        # Provider NPI (10 digits)
        npi_match = re.search(r'(?:provider\s+)?NPI[:\s#]+(\d{10})', text, re.IGNORECASE)
        if npi_match:
            info.provider_npi = npi_match.group(1)
        
        # Facility NPI
        facility_npi_match = re.search(r'facility\s+NPI[:\s#]+(\d{10})', text, re.IGNORECASE)
        if facility_npi_match:
            info.facility_npi = facility_npi_match.group(1)
        
        # Tax ID / EIN
        tax_match = re.search(r'(?:tax\s+id|ein)[:\s#]+(\d{2}-?\d{7})', text, re.IGNORECASE)
        if tax_match:
            info.tax_id = tax_match.group(1)
        
        return info
    
    def _extract_diagnosis_codes(self, text: str) -> List[DiagnosisCode]:
        """Extract ICD-10 diagnosis codes"""
        
        codes = []
        
        # ICD-10 pattern (e.g., J20.9, E11.9, I10)
        icd_pattern = r'\b([A-Z]\d{2}(?:\.\d{1,2})?)\b'
        
        for match in re.finditer(icd_pattern, text):
            code = match.group(1)
            
            # Basic validation (ICD-10 starts with letter)
            if code[0].isalpha():
                codes.append(DiagnosisCode(
                    code=code,
                    source_span=match.group(0),
                    confidence=0.7  # Lower confidence for regex extraction
                ))
        
        return codes
    
    def _extract_procedure_codes(self, text: str) -> List[ProcedureCode]:
        """Extract CPT/HCPCS procedure codes"""
        
        codes = []
        
        # CPT pattern (5 digits, optionally with modifier)
        cpt_pattern = r'\b(\d{5})(?:-([A-Z0-9]{2}))?\b'
        
        for match in re.finditer(cpt_pattern, text):
            code = match.group(1)
            modifier = match.group(2) if match.group(2) else None
            
            # Try to find charge associated with this code
            charge = None
            # Look for pattern like "99214: $185.00" or "99214 - $185.00"
            charge_pattern = rf'{code}[:\-\s]+\$?([\d,]+\.?\d{{0,2}})'
            charge_match = re.search(charge_pattern, text)
            if charge_match:
                charge_str = charge_match.group(1).replace(',', '')
                charge = float(charge_str)
            # Try to capture a description on the same line after the code
            description = None
            # get the rest of the line after the match
            line_rest = text[match.end():].split('\n', 1)[0]
            if line_rest:
                # strip common separators and numbering
                desc = re.sub(r'^[\s\-:\.)]+', '', line_rest).strip()
                # If the description starts with a hyphen or digits (like list numbers), strip them
                desc = re.sub(r'^[0-9\.\)\-\s]+', '', desc).strip()
                # Only accept as description if contains letters
                if re.search(r'[A-Za-z]', desc):
                    # Limit description length
                    description = desc.strip()

            codes.append(ProcedureCode(
                code=code,
                modifier=modifier,
                charge=charge,
                description=description,
                confidence=0.7
            ))
        
        return codes
    
    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract important dates"""
        
        dates = {}
        
        # Date of service
        dos_match = re.search(
            r'(?:date\s+of\s+service|service\s+date|dos)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            text,
            re.IGNORECASE
        )
        if dos_match:
            dates['service_date'] = self._normalize_date(dos_match.group(1))
        
        return dates
    
    def _extract_amounts(self, text: str) -> Dict[str, float]:
        """Extract monetary amounts"""
        
        amounts = {}
        
        # Total charges
        charge_match = re.search(
            r'(?:total\s+)?(?:charge|amount)[:\s]+\$?([\d,]+\.?\d{0,2})',
            text,
            re.IGNORECASE
        )
        if charge_match:
            amount_str = charge_match.group(1).replace(',', '')
            amounts['total_charge'] = float(amount_str)
        
        return amounts
    
    def _llm_extract(self, text: str) -> Dict[str, Any]:
        """Use LLM to extract structured data"""
        
        from llm.ollama import OllamaClient
        
        client = OllamaClient()
        
        # Load extraction prompt
        from llm.prompts.extract_notes import EXTRACTION_PROMPT
        
        prompt = EXTRACTION_PROMPT.format(text=text)
        
        result = client.structured_extraction(
            prompt=prompt,
            schema={
                "patient": {"type": "object"},
                "insurance": {"type": "object"},
                "provider": {"type": "object"},
                "diagnoses": {"type": "array"},
                "procedures": {"type": "array"}
            }
        )
        
        return result
    
    def _merge_patient_info(self, base: PatientInfo, llm_data: Optional[Dict]) -> PatientInfo:
        """Merge LLM-extracted patient data with rule-based"""
        
        if not llm_data:
            return base
        
        # LLM data fills in missing fields
        for field in PatientInfo.__fields__:
            if not getattr(base, field) and field in llm_data:
                setattr(base, field, llm_data[field])
        
        return base
    
    def _merge_insurance_info(self, base: InsuranceInfo, llm_data: Optional[Dict]) -> InsuranceInfo:
        """Merge insurance data"""
        if not llm_data:
            return base
        for field in InsuranceInfo.__fields__:
            if not getattr(base, field) and field in llm_data:
                setattr(base, field, llm_data[field])
        return base
    
    def _merge_provider_info(self, base: ProviderInfo, llm_data: Optional[Dict]) -> ProviderInfo:
        """Merge provider data"""
        if not llm_data:
            return base
        for field in ProviderInfo.__fields__:
            if not getattr(base, field) and field in llm_data:
                setattr(base, field, llm_data[field])
        return base
    
    def _calculate_confidence(
        self,
        patient: PatientInfo,
        insurance: InsuranceInfo,
        provider: ProviderInfo,
        diagnoses: List[DiagnosisCode],
        procedures: List[ProcedureCode]
    ) -> float:
        """Calculate overall extraction confidence"""
        
        # Count filled fields
        patient_fields = sum(1 for f in ['first_name', 'last_name', 'dob'] if getattr(patient, f))
        insurance_fields = sum(1 for f in ['insurance_name', 'policy_number'] if getattr(insurance, f))
        provider_fields = sum(1 for f in ['provider_npi'] if getattr(provider, f))
        
        total_critical_fields = 6  # 3 patient + 2 insurance + 1 provider
        filled_critical = patient_fields + insurance_fields + provider_fields
        
        field_score = filled_critical / total_critical_fields
        
        # Bonus for codes
        code_score = min((len(diagnoses) + len(procedures)) / 5.0, 0.2)
        
        return min(field_score + code_score, 1.0)
    
    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format"""
        
        # Try common formats
        for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str  # Return as-is if can't parse


def format_extracted_data_for_qa(extracted_data: ExtractedData) -> str:
    """
    Format ExtractedData into a readable string for Q&A context.
    
    Args:
        extracted_data: ExtractedData object to format
        
    Returns:
        Formatted string containing all extracted information
    """
    lines = []
    
    # Patient Information
    lines.append("=== PATIENT INFORMATION ===")
    if extracted_data.patient:
        patient = extracted_data.patient
        if patient.first_name or patient.last_name:
            name_parts = [p for p in [patient.first_name, patient.middle_name, patient.last_name] if p]
            lines.append(f"Name: {' '.join(name_parts)}")
        if patient.dob:
            lines.append(f"Date of Birth: {patient.dob}")
        if patient.sex:
            lines.append(f"Sex: {patient.sex}")
        if patient.address:
            address_parts = [patient.address]
            if patient.city:
                address_parts.append(patient.city)
            if patient.state:
                address_parts.append(patient.state)
            if patient.zip_code:
                address_parts.append(patient.zip_code)
            lines.append(f"Address: {', '.join(address_parts)}")
        if patient.phone:
            lines.append(f"Phone: {patient.phone}")
        if patient.marital_status:
            lines.append(f"Marital Status: {patient.marital_status}")
        if patient.employment_status:
            lines.append(f"Employment Status: {patient.employment_status}")
    else:
        lines.append("No patient information available")
    
    lines.append("")
    
    # Insurance Information
    lines.append("=== INSURANCE INFORMATION ===")
    if extracted_data.insurance:
        insurance = extracted_data.insurance
        if insurance.insurance_name:
            lines.append(f"Insurance Name: {insurance.insurance_name}")
        if insurance.plan_name:
            lines.append(f"Plan Name: {insurance.plan_name}")
        if insurance.policy_number:
            lines.append(f"Policy Number: {insurance.policy_number}")
        if insurance.group_number:
            lines.append(f"Group Number: {insurance.group_number}")
        if insurance.subscriber_name:
            lines.append(f"Subscriber Name: {insurance.subscriber_name}")
        if insurance.subscriber_relationship:
            lines.append(f"Subscriber Relationship: {insurance.subscriber_relationship}")
        if insurance.subscriber_dob:
            lines.append(f"Subscriber DOB: {insurance.subscriber_dob}")
        if insurance.payer_id:
            lines.append(f"Payer ID: {insurance.payer_id}")
    else:
        lines.append("No insurance information available")
    
    lines.append("")
    
    # Provider Information
    lines.append("=== PROVIDER INFORMATION ===")
    if extracted_data.provider:
        provider = extracted_data.provider
        if provider.provider_name:
            lines.append(f"Provider Name: {provider.provider_name}")
        if provider.provider_npi:
            lines.append(f"Provider NPI: {provider.provider_npi}")
        if provider.facility_name:
            lines.append(f"Facility Name: {provider.facility_name}")
        if provider.facility_npi:
            lines.append(f"Facility NPI: {provider.facility_npi}")
        if provider.facility_address:
            address_parts = [provider.facility_address]
            if provider.facility_city:
                address_parts.append(provider.facility_city)
            if provider.facility_state:
                address_parts.append(provider.facility_state)
            if provider.facility_zip:
                address_parts.append(provider.facility_zip)
            lines.append(f"Facility Address: {', '.join(address_parts)}")
        if provider.phone:
            lines.append(f"Phone: {provider.phone}")
        if provider.tax_id:
            lines.append(f"Tax ID: {provider.tax_id}")
    else:
        lines.append("No provider information available")
    
    lines.append("")
    
    # Diagnoses
    lines.append("=== DIAGNOSES ===")
    if extracted_data.diagnoses:
        for i, dx in enumerate(extracted_data.diagnoses, 1):
            dx_line = f"{i}. {dx.code}"
            if dx.description:
                dx_line += f" - {dx.description}"
            if dx.letter:
                dx_line += f" (Letter: {dx.letter})"
            if dx.confidence < 1.0:
                dx_line += f" [Confidence: {dx.confidence:.0%}]"
            lines.append(dx_line)
    else:
        lines.append("No diagnoses found")
    
    lines.append("")
    
    # Procedures
    lines.append("=== PROCEDURES ===")
    if extracted_data.procedures:
        for i, proc in enumerate(extracted_data.procedures, 1):
            proc_line = f"{i}. {proc.code}"
            if proc.description:
                proc_line += f" - {proc.description}"
            if proc.modifier:
                proc_line += f" (Modifier: {proc.modifier})"
            if proc.units > 1:
                proc_line += f" (Units: {proc.units})"
            if proc.charge:
                proc_line += f" - Charge: ${proc.charge:,.2f}"
            if proc.date_of_service:
                proc_line += f" (Date: {proc.date_of_service})"
            if proc.diagnosis_pointers:
                proc_line += f" [Diagnosis Pointers: {', '.join(proc.diagnosis_pointers)}]"
            if proc.confidence < 1.0:
                proc_line += f" [Confidence: {proc.confidence:.0%}]"
            lines.append(proc_line)
    else:
        lines.append("No procedures found")
    
    lines.append("")
    
    # Dates
    lines.append("=== IMPORTANT DATES ===")
    if extracted_data.dates:
        for key, value in extracted_data.dates.items():
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
    else:
        lines.append("No dates extracted")
    
    lines.append("")
    
    # Amounts
    lines.append("=== FINANCIAL INFORMATION ===")
    if extracted_data.amounts:
        for key, value in extracted_data.amounts.items():
            lines.append(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
    else:
        lines.append("No financial amounts extracted")
    
    lines.append("")
    
    # Metadata
    if extracted_data.metadata:
        lines.append("=== METADATA ===")
        for key, value in extracted_data.metadata.items():
            lines.append(f"{key}: {value}")
        lines.append("")
    
    lines.append(f"Extraction Confidence: {extracted_data.extraction_confidence:.0%}")
    
    return "\n".join(lines)


def extract_patient_data(text: str, use_llm: bool = True) -> Dict[str, Any]:
    """
    Convenience function to extract patient data from text.
    
    Args:
        text: Source text
        use_llm: Use LLM enhancement
        
    Returns:
        Dictionary with extracted data
    """
    extractor = DataExtractor(use_llm=use_llm)
    result = extractor.extract(text)
    return result.model_dump()
