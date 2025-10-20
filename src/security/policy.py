"""
HIPAA Policy Enforcement Module
Implements minimum necessary, data retention, and consent management.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from enum import Enum


class ConsentType(str, Enum):
    """Types of consent"""
    TREATMENT = "treatment"
    PAYMENT = "payment"
    OPERATIONS = "operations"
    LLM_PROCESSING = "llm_processing"
    DATA_SHARING = "data_sharing"


class PolicyManager:
    """
    HIPAA policy enforcement.
    
    Implements:
    - Minimum Necessary Rule (164.502(b))
    - Data Retention policies
    - Consent management
    - PHI minimization
    
    Configuration controlled via environment/settings.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load configuration (from env/settings)
        import os
        self.minimum_necessary_enabled = os.getenv("MINIMUM_NECESSARY_MODE", "true").lower() == "true"
        self.retention_days = int(os.getenv("PHI_RETENTION_DAYS", "90"))
        
        # Consent registry (in-memory, production would use database)
        self.consents: Dict[str, Set[ConsentType]] = {}
    
    def apply_minimum_necessary(
        self,
        data: Dict[str, Any],
        purpose: str,
        user_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply minimum necessary rule to PHI.
        
        Redacts fields not required for the specified purpose.
        
        Args:
            data: PHI data
            purpose: Purpose (treatment, payment, operations, etc.)
            user_role: User role accessing data
            
        Returns:
            Filtered data with only necessary fields
        """
        if not self.minimum_necessary_enabled:
            self.logger.info("Minimum necessary mode disabled, returning full data")
            return data
        
        # Define fields required for each purpose
        purpose_fields = {
            "treatment": [
                "patient_name", "patient_dob", "diagnoses", "procedures",
                "clinical_notes", "medications", "allergies"
            ],
            "payment": [
                "patient_name", "patient_id", "insurance_info",
                "diagnoses", "procedures", "charges", "dates_of_service"
            ],
            "operations": [
                "patient_id", "diagnoses", "procedures", "outcomes"
            ],
            "llm_processing": [
                "clinical_notes", "diagnoses_codes", "procedure_codes"
            ],
            "reporting": [
                "patient_id", "age", "diagnoses", "procedures", "outcomes"
            ]
        }
        
        required_fields = purpose_fields.get(purpose, [])
        
        # Filter data
        filtered = {}
        for field in required_fields:
            if field in data:
                filtered[field] = data[field]
        
        self.logger.info(f"Applied minimum necessary for purpose '{purpose}': {len(filtered)}/{len(data)} fields")
        
        return filtered
    
    def redact_for_llm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PHI before sending to LLM.
        
        Removes direct identifiers per HIPAA Safe Harbor method.
        
        Args:
            data: Data to redact
            
        Returns:
            Redacted data
        """
        # Fields to redact (HIPAA identifiers)
        redact_fields = [
            "patient_name",
            "patient_address",
            "phone",
            "email",
            "ssn",
            "mrn",  # Medical record number
            "account_number",
            "fax",
            "ip_address",
            "url",
            "full_face_photo",
            "biometric_id",
            "vehicle_id",
            "device_id"
        ]
        
        redacted = data.copy()
        
        for field in redact_fields:
            if field in redacted:
                redacted[field] = "[REDACTED]"
        
        # Generalize dates to year only
        date_fields = ["dob", "admission_date", "discharge_date"]
        for field in date_fields:
            if field in redacted and isinstance(redacted[field], str):
                # Extract year only
                try:
                    year = redacted[field].split('-')[0]
                    redacted[field] = year
                except:
                    redacted[field] = "[DATE]"
        
        self.logger.info(f"Redacted {len(redact_fields)} PHI fields for LLM processing")
        
        return redacted
    
    def check_consent(self, patient_id: str, consent_type: ConsentType) -> bool:
        """
        Check if patient has given consent.
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent required
            
        Returns:
            True if consent granted
        """
        patient_consents = self.consents.get(patient_id, set())
        return consent_type in patient_consents
    
    def record_consent(
        self,
        patient_id: str,
        consent_type: ConsentType,
        granted: bool = True
    ):
        """
        Record patient consent.
        
        Args:
            patient_id: Patient identifier
            consent_type: Type of consent
            granted: True to grant, False to revoke
        """
        if patient_id not in self.consents:
            self.consents[patient_id] = set()
        
        if granted:
            self.consents[patient_id].add(consent_type)
            self.logger.info(f"Consent granted: {patient_id} for {consent_type.value}")
        else:
            self.consents[patient_id].discard(consent_type)
            self.logger.info(f"Consent revoked: {patient_id} for {consent_type.value}")
    
    def should_retain(self, record_date: datetime) -> bool:
        """
        Check if record should be retained based on retention policy.
        
        Args:
            record_date: Date record was created
            
        Returns:
            True if should retain, False if eligible for deletion
        """
        age = datetime.now() - record_date
        return age.days < self.retention_days
    
    def get_retention_deadline(self, record_date: datetime) -> datetime:
        """Get date when record can be deleted"""
        return record_date + timedelta(days=self.retention_days)


# Global policy manager
_policy_manager = None


def get_policy_manager() -> PolicyManager:
    """Get or create global policy manager"""
    global _policy_manager
    if _policy_manager is None:
        _policy_manager = PolicyManager()
    return _policy_manager
