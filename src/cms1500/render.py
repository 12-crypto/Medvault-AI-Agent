"""
CMS-1500 Rendering Module
Renders claims for UI preview and export.
"""

from typing import Dict, Any, List
from cms1500.schema import CMS1500Claim


class CMS1500Renderer:
    """Render CMS-1500 claims for display and export"""
    
    def render_for_display(self, claim: CMS1500Claim) -> Dict[str, Any]:
        """
        Render claim as structured dict for UI display.
        
        Returns:
            Dictionary organized by sections for easy display
        """
        return {
            "carrier": self._render_carrier(claim),
            "patient_info": self._render_patient_info(claim),
            "insurance_info": self._render_insurance_info(claim),
            "condition_info": self._render_condition_info(claim),
            "diagnoses": self._render_diagnoses(claim),
            "service_lines": self._render_service_lines(claim),
            "provider_info": self._render_provider_info(claim),
            "totals": self._render_totals(claim)
        }
    
    def _render_carrier(self, claim: CMS1500Claim) -> Dict[str, str]:
        """Render carrier information"""
        return {
            "name": claim.carrier_name or "",
            "address": claim.carrier_address or "",
            "city_state_zip": claim.carrier_city_state_zip or ""
        }
    
    def _render_patient_info(self, claim: CMS1500Claim) -> Dict[str, str]:
        """Render patient demographic information"""
        return {
            "name": f"{claim.patient_last_name}, {claim.patient_first_name}",
            "dob": claim.patient_dob,
            "sex": claim.patient_sex,
            "address": claim.patient_address or "",
            "city": claim.patient_city or "",
            "state": claim.patient_state or "",
            "zip": claim.patient_zip or "",
            "phone": claim.patient_phone or ""
        }
    
    def _render_insurance_info(self, claim: CMS1500Claim) -> Dict[str, Any]:
        """Render insurance information"""
        relationship = "Self"
        if claim.patient_relationship_spouse:
            relationship = "Spouse"
        elif claim.patient_relationship_child:
            relationship = "Child"
        elif claim.patient_relationship_other:
            relationship = "Other"
        
        return {
            "insured_id": claim.insured_id_number,
            "insured_name": claim.insured_name or "Same as Patient",
            "relationship": relationship,
            "policy_group": claim.insured_policy_group or "",
            "plan_name": claim.insurance_plan_name or ""
        }
    
    def _render_condition_info(self, claim: CMS1500Claim) -> Dict[str, Any]:
        """Render condition-related information"""
        return {
            "employment_related": claim.condition_related_employment or False,
            "auto_accident": claim.condition_related_auto_accident or False,
            "auto_accident_state": claim.auto_accident_state or "",
            "other_accident": claim.condition_related_other_accident or False
        }
    
    def _render_diagnoses(self, claim: CMS1500Claim) -> List[Dict[str, str]]:
        """Render diagnosis codes"""
        diagnoses = []
        for letter in 'ABCDEFGHIJKL':
            code = claim.get_diagnosis_by_letter(letter)
            if code:
                diagnoses.append({
                    "letter": letter,
                    "code": code
                })
        return diagnoses
    
    def _render_service_lines(self, claim: CMS1500Claim) -> List[Dict[str, Any]]:
        """Render service line details"""
        lines = []
        for idx, line in enumerate(claim.service_lines, start=1):
            modifiers = []
            for mod in [line.modifier1, line.modifier2, line.modifier3, line.modifier4]:
                if mod:
                    modifiers.append(mod)
            
            lines.append({
                "line_number": idx,
                "date_from": line.date_from,
                "date_to": line.date_to or line.date_from,
                "place_of_service": line.place_of_service,
                "cpt_hcpcs": line.cpt_hcpcs,
                "modifiers": modifiers,
                "diagnosis_pointer": line.diagnosis_pointer,
                "charges": f"${line.charges:.2f}",
                "units": line.days_or_units,
                "rendering_provider": line.rendering_provider_id or ""
            })
        return lines
    
    def _render_provider_info(self, claim: CMS1500Claim) -> Dict[str, Any]:
        """Render provider information"""
        return {
            "billing_provider": {
                "name": claim.billing_provider_name or "",
                "npi": claim.billing_provider_npi or "",
                "address": claim.billing_provider_address or "",
                "city": claim.billing_provider_city or "",
                "state": claim.billing_provider_state or "",
                "zip": claim.billing_provider_zip or "",
                "phone": claim.billing_provider_phone or ""
            },
            "service_facility": {
                "name": claim.service_facility_name or "",
                "npi": claim.service_facility_npi or "",
                "address": claim.service_facility_address or ""
            },
            "referring_provider": {
                "name": claim.referring_provider_name or "",
                "npi": claim.referring_provider_npi or ""
            }
        }
    
    def _render_totals(self, claim: CMS1500Claim) -> Dict[str, str]:
        """Render financial totals"""
        return {
            "total_charge": f"${claim.total_charge:.2f}",
            "amount_paid": f"${claim.amount_paid:.2f}" if claim.amount_paid else "$0.00",
            "balance_due": f"${claim.balance_due:.2f}" if claim.balance_due else f"${claim.total_charge:.2f}"
        }


def render_claim(claim: CMS1500Claim) -> Dict[str, Any]:
    """
    Convenience function to render a claim.
    
    Args:
        claim: CMS1500Claim object
        
    Returns:
        Rendered claim dictionary
    """
    renderer = CMS1500Renderer()
    return renderer.render_for_display(claim)
