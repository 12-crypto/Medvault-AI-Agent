"""
CMS-1500 Claim Generator
Generates CMS-1500 claims from extracted data and coding results.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .schema import CMS1500Claim, ServiceLineInfo, ICDIndicator
from ..core.extraction import ExtractedData, PatientInfo, InsuranceInfo, ProviderInfo
from ..core.coding import CodingResult

logger = logging.getLogger(__name__)


class CMS1500Generator:
    """
    Generate CMS-1500 claims from extracted and coded data.
    
    Maps extracted patient/insurance/provider info and medical codes
    to CMS-1500 form fields according to NUCC specifications.
    """
    
    def create_claim(
        self,
        extracted_data: Optional[ExtractedData] = None,
        coding_result: Optional[CodingResult] = None,
        patient_info: Optional[PatientInfo] = None,
        insurance_info: Optional[InsuranceInfo] = None,
        provider_info: Optional[ProviderInfo] = None,
        **overrides
    ) -> CMS1500Claim:
        """
        Create a CMS-1500 claim from various data sources.
        
        Args:
            extracted_data: Complete extracted data object
            coding_result: Medical coding results
            patient_info: Patient information (alternative to extracted_data)
            insurance_info: Insurance information
            provider_info: Provider information
            **overrides: Direct field overrides
            
        Returns:
            CMS1500Claim object
        """
        # Extract components if extracted_data provided
        if extracted_data:
            patient_info = extracted_data.patient
            insurance_info = extracted_data.insurance
            provider_info = extracted_data.provider
        
        # Build claim dictionary
        claim_data = {}
        
        # Map patient info (Items 2, 3, 5)
        if patient_info:
            claim_data.update(self._map_patient_info(patient_info))
        
        # Map insurance info (Items 1, 1a, 4, 9-11)
        if insurance_info:
            claim_data.update(self._map_insurance_info(insurance_info, patient_info))
        
        # Map provider info (Items 17, 32, 33)
        if provider_info:
            claim_data.update(self._map_provider_info(provider_info))
        
        # Map diagnoses (Item 21)
        if coding_result:
            claim_data.update(self._map_diagnoses(coding_result))
            # Map service lines (Item 24)
            claim_data.update(self._map_service_lines(coding_result))
        
        # Apply overrides
        claim_data.update(overrides)
        
        # Set defaults
        claim_data.setdefault('icd_indicator', ICDIndicator.ICD10)
        claim_data.setdefault('created_at', datetime.now())
        
        # Create claim
        return CMS1500Claim(**claim_data)
    
    def _map_patient_info(self, patient: PatientInfo) -> Dict[str, Any]:
        """Map patient info to CMS-1500 fields"""
        
        data = {}
        
        # Item 2: Patient name
        if patient.last_name:
            data['patient_last_name'] = patient.last_name
        if patient.first_name:
            data['patient_first_name'] = patient.first_name
        if patient.middle_name:
            data['patient_middle_initial'] = patient.middle_name[0] if patient.middle_name else None
        
        # Item 3: DOB and sex
        if patient.dob:
            # Convert YYYY-MM-DD to MM DD YYYY
            dob_parts = patient.dob.split('-')
            if len(dob_parts) == 3:
                data['patient_dob'] = f"{dob_parts[1]} {dob_parts[2]} {dob_parts[0]}"
        if patient.sex:
            data['patient_sex'] = patient.sex
        
        # Item 5: Patient address
        if patient.address:
            data['patient_address'] = patient.address
        if patient.city:
            data['patient_city'] = patient.city
        if patient.state:
            data['patient_state'] = patient.state
        if patient.zip_code:
            data['patient_zip'] = patient.zip_code
        if patient.phone:
            data['patient_phone'] = patient.phone
        
        return data
    
    def _map_insurance_info(self, insurance: InsuranceInfo, patient: Optional[PatientInfo]) -> Dict[str, Any]:
        """Map insurance info to CMS-1500 fields"""
        
        data = {}
        
        # Item 1a: Insured's ID
        if insurance.policy_number:
            data['insured_id_number'] = insurance.policy_number
        
        # Item 4: Insured's name (if not self)
        if insurance.subscriber_name:
            data['insured_name'] = insurance.subscriber_name
        
        # Item 6: Patient relationship to insured
        relationship = insurance.subscriber_relationship or 'Self'
        data['patient_relationship_self'] = relationship.lower() == 'self'
        data['patient_relationship_spouse'] = relationship.lower() == 'spouse'
        data['patient_relationship_child'] = relationship.lower() == 'child'
        data['patient_relationship_other'] = relationship.lower() not in ['self', 'spouse', 'child']
        
        # Item 11: Insurance plan info
        if insurance.insurance_name:
            data['insurance_plan_name'] = insurance.insurance_name
        if insurance.group_number:
            data['insured_policy_group'] = insurance.group_number
        
        # If insurance is for patient (self), fill Item 7 from patient address
        if data.get('patient_relationship_self') and patient:
            data['insured_address'] = patient.address
            data['insured_city'] = patient.city
            data['insured_state'] = patient.state
            data['insured_zip'] = patient.zip_code
            data['insured_phone'] = patient.phone
        
        return data
    
    def _map_provider_info(self, provider: ProviderInfo) -> Dict[str, Any]:
        """Map provider info to CMS-1500 fields"""
        
        data = {}
        
        # Item 17: Referring provider
        if provider.provider_name:
            data['referring_provider_name'] = provider.provider_name
        if provider.provider_npi:
            data['referring_provider_npi'] = provider.provider_npi
        
        # Item 25: Tax ID
        if provider.tax_id:
            data['federal_tax_id'] = provider.tax_id
            # Detect if SSN or EIN based on format
            if '-' in provider.tax_id:
                parts = provider.tax_id.split('-')
                if len(parts) == 3:
                    data['tax_id_type_ssn'] = True
                elif len(parts) == 2:
                    data['tax_id_type_ein'] = True
            else:
                data['tax_id_type_ein'] = True  # Default assumption
        
        # Item 32: Service facility
        if provider.facility_name:
            data['service_facility_name'] = provider.facility_name
        if provider.facility_npi:
            data['service_facility_npi'] = provider.facility_npi
        if provider.facility_address:
            data['service_facility_address'] = provider.facility_address
        if provider.facility_city:
            data['service_facility_city'] = provider.facility_city
        if provider.facility_state:
            data['service_facility_state'] = provider.facility_state
        if provider.facility_zip:
            data['service_facility_zip'] = provider.facility_zip
        
        # Item 33: Billing provider (use facility if no separate billing provider)
        data['billing_provider_name'] = provider.facility_name or provider.provider_name
        data['billing_provider_npi'] = provider.facility_npi or provider.provider_npi
        data['billing_provider_address'] = provider.facility_address
        data['billing_provider_city'] = provider.facility_city
        data['billing_provider_state'] = provider.facility_state
        data['billing_provider_zip'] = provider.facility_zip
        data['billing_provider_phone'] = provider.phone
        
        return data
    
    def _map_diagnoses(self, coding_result: CodingResult) -> Dict[str, Any]:
        """Map diagnosis codes to Item 21"""
        
        data = {
            'icd_indicator': ICDIndicator.ICD10
        }
        
        # Map up to 12 diagnoses (A-L)
        letters = 'abcdefghijkl'
        for idx, (letter, dx_letter) in enumerate(zip(letters, coding_result.diagnosis_letters.keys())):
            dx_code = None
            for dx in coding_result.diagnoses:
                if dx.code == dx_letter:
                    dx_code = dx.code
                    break
            if dx_code:
                data[f'diagnosis_{letter}'] = dx_code
        
        return data
    
    def _map_service_lines(self, coding_result: CodingResult) -> Dict[str, Any]:
        """Map procedure codes to Item 24 service lines"""
        
        service_lines = []
        
        for proc in coding_result.procedures[:6]:  # Max 6 lines
            # Get diagnosis pointers from metadata
            dx_pointers = proc.metadata.get('diagnosis_pointers', []) if proc.metadata else []
            diagnosis_pointer = ''.join(dx_pointers) if dx_pointers else 'A'
            
            # Parse code and modifier
            code_parts = proc.code.split('-')
            cpt_code = code_parts[0]
            modifier = code_parts[1] if len(code_parts) > 1 else None
            
            line = ServiceLineInfo(
                date_from=self._format_date_for_cms(datetime.now()),  # Should come from extracted data
                place_of_service="11",  # Office (default)
                cpt_hcpcs=cpt_code,
                modifier1=modifier,
                diagnosis_pointer=diagnosis_pointer,
                charges=100.00,  # Should come from extracted data
                days_or_units=1
            )
            service_lines.append(line)
        
        # Calculate total
        total_charge = sum(line.charges * line.days_or_units for line in service_lines)
        
        return {
            'service_lines': service_lines,
            'total_charge': total_charge
        }
    
    @staticmethod
    def _format_date_for_cms(dt: datetime) -> str:
        """Format datetime to MM DD YYYY"""
        return dt.strftime("%m %d %Y")


def generate_claim(extracted_data: ExtractedData, coding_result: CodingResult) -> CMS1500Claim:
    """
    Convenience function to generate a claim.
    
    Args:
        extracted_data: Extracted patient/insurance/provider data
        coding_result: Medical coding results
        
    Returns:
        CMS1500Claim object
    """
    generator = CMS1500Generator()
    return generator.create_claim(extracted_data=extracted_data, coding_result=coding_result)
