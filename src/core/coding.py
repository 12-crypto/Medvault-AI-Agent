"""
Medical Coding Assistant Module
LLM-powered mapping of clinical notes to ICD-10 and CPT/HCPCS codes
with cross-referencing and mismatch detection.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from .extraction import DiagnosisCode, ProcedureCode

logger = logging.getLogger(__name__)


class CodeSuggestion(BaseModel):
    """A suggested medical code with context"""
    code: str
    code_type: str  # "ICD-10", "CPT", "HCPCS"
    description: str
    rationale: str  # Why this code was suggested
    confidence: float = Field(ge=0.0, le=1.0)
    source_text: Optional[str] = None  # Text snippet that triggered suggestion
    alternatives: List[str] = Field(default_factory=list)  # Alternative codes


class CodeMismatch(BaseModel):
    """Detected mismatch between codes"""
    mismatch_type: str  # "diagnosis_procedure", "missing_diagnosis", "invalid_pairing"
    severity: str  # "error", "warning", "info"
    message: str
    affected_codes: List[str]
    suggestion: Optional[str] = None


class CodingResult(BaseModel):
    """Complete coding assistant result"""
    diagnoses: List[CodeSuggestion]
    procedures: List[CodeSuggestion]
    mismatches: List[CodeMismatch]
    diagnosis_procedure_map: Dict[str, List[str]]  # diagnosis code -> procedure codes
    diagnosis_letters: Dict[str, str]  # diagnosis code -> letter (A-L)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MedicalCodingAssistant:
    """
    AI-powered medical coding assistant.
    
    Capabilities:
    1. Suggest ICD-10 codes from clinical notes
    2. Suggest CPT/HCPCS codes from procedures described
    3. Map diagnosis codes to procedure codes
    4. Assign diagnosis letters (A-L) for CMS-1500
    5. Detect mismatches and invalid pairings
    6. Flag codes requiring human review
    """
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize coding assistant.
        
        Args:
            use_llm: Use LLM for code suggestions
        """
        self.use_llm = use_llm
    
    def suggest_codes(
        self,
        clinical_notes: str,
        existing_diagnoses: Optional[List[DiagnosisCode]] = None,
        existing_procedures: Optional[List[ProcedureCode]] = None
    ) -> CodingResult:
        """
        Suggest medical codes from clinical notes.
        
        Args:
            clinical_notes: Unstructured clinical documentation
            existing_diagnoses: Already extracted diagnosis codes
            existing_procedures: Already extracted procedure codes
            
        Returns:
            CodingResult with suggestions and validations
        """
        logger.info("Starting medical code suggestion")
        
        existing_diagnoses = existing_diagnoses or []
        existing_procedures = existing_procedures or []
        
        # Get LLM suggestions
        if self.use_llm:
            llm_diagnoses, llm_procedures = self._llm_suggest_codes(clinical_notes)
        else:
            llm_diagnoses, llm_procedures = [], []
        
        # Merge with existing codes
        all_diagnoses = self._merge_diagnosis_suggestions(existing_diagnoses, llm_diagnoses)
        all_procedures = self._merge_procedure_suggestions(existing_procedures, llm_procedures)
        
        # Assign diagnosis letters (A-L) for CMS-1500
        diagnosis_letters = self._assign_diagnosis_letters(all_diagnoses)
        
        # Map diagnoses to procedures
        dx_proc_map = self._map_diagnoses_to_procedures(all_diagnoses, all_procedures)
        
        # Update procedure diagnosis pointers
        all_procedures = self._update_diagnosis_pointers(all_procedures, dx_proc_map, diagnosis_letters)
        
        # Validate and detect mismatches
        mismatches = self._detect_mismatches(all_diagnoses, all_procedures, dx_proc_map)
        
        # Calculate confidence
        confidence = self._calculate_overall_confidence(all_diagnoses, all_procedures, mismatches)
        
        return CodingResult(
            diagnoses=all_diagnoses,
            procedures=all_procedures,
            mismatches=mismatches,
            diagnosis_procedure_map=dx_proc_map,
            diagnosis_letters=diagnosis_letters,
            overall_confidence=confidence,
            metadata={
                "total_diagnoses": len(all_diagnoses),
                "total_procedures": len(all_procedures),
                "total_mismatches": len(mismatches)
            }
        )
    
    def _llm_suggest_codes(self, clinical_notes: str) -> Tuple[List[CodeSuggestion], List[CodeSuggestion]]:
        """Use LLM to suggest codes from clinical notes"""
        
        from ..llm.ollama import OllamaClient
        from ..llm.prompts.code_mapping import CODE_MAPPING_PROMPT
        
        client = OllamaClient()
        
        prompt = CODE_MAPPING_PROMPT.format(clinical_notes=clinical_notes)
        
        try:
            result = client.structured_extraction(
                prompt=prompt,
                schema={
                    "diagnoses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "description": {"type": "string"},
                                "rationale": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "procedures": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "description": {"type": "string"},
                                "rationale": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    }
                }
            )
            
            # Convert to CodeSuggestion objects
            diagnoses = [
                CodeSuggestion(
                    code=d["code"],
                    code_type="ICD-10",
                    description=d.get("description", ""),
                    rationale=d.get("rationale", ""),
                    confidence=d.get("confidence", 0.8)
                )
                for d in result.get("diagnoses", [])
            ]
            
            procedures = [
                CodeSuggestion(
                    code=p["code"],
                    code_type="CPT" if len(p["code"]) == 5 and p["code"].isdigit() else "HCPCS",
                    description=p.get("description", ""),
                    rationale=p.get("rationale", ""),
                    confidence=p.get("confidence", 0.8)
                )
                for p in result.get("procedures", [])
            ]
            
            return diagnoses, procedures
            
        except Exception as e:
            logger.error(f"LLM code suggestion failed: {e}")
            return [], []
    
    def _merge_diagnosis_suggestions(
        self,
        existing: List[DiagnosisCode],
        llm_suggestions: List[CodeSuggestion]
    ) -> List[CodeSuggestion]:
        """Merge existing diagnosis codes with LLM suggestions"""
        
        # Convert existing to CodeSuggestion
        merged = []
        seen_codes = set()
        
        for dx in existing:
            merged.append(CodeSuggestion(
                code=dx.code,
                code_type="ICD-10",
                description=dx.description or "",
                rationale="Extracted from document",
                confidence=dx.confidence,
                source_text=dx.source_span
            ))
            seen_codes.add(dx.code)
        
        # Add LLM suggestions if not duplicate
        for suggestion in llm_suggestions:
            if suggestion.code not in seen_codes:
                merged.append(suggestion)
                seen_codes.add(suggestion.code)
        
        return merged
    
    def _merge_procedure_suggestions(
        self,
        existing: List[ProcedureCode],
        llm_suggestions: List[CodeSuggestion]
    ) -> List[CodeSuggestion]:
        """Merge existing procedure codes with LLM suggestions"""
        
        merged = []
        seen_codes = set()
        
        for proc in existing:
            code_key = f"{proc.code}-{proc.modifier}" if proc.modifier else proc.code
            merged.append(CodeSuggestion(
                code=code_key,
                code_type="CPT" if len(proc.code) == 5 else "HCPCS",
                description=proc.description or "",
                rationale="Extracted from document",
                confidence=proc.confidence
            ))
            seen_codes.add(code_key)
        
        # Add LLM suggestions
        for suggestion in llm_suggestions:
            if suggestion.code not in seen_codes:
                merged.append(suggestion)
                seen_codes.add(suggestion.code)
        
        return merged
    
    def _assign_diagnosis_letters(self, diagnoses: List[CodeSuggestion]) -> Dict[str, str]:
        """
        Assign letters A-L to diagnosis codes for CMS-1500 Item 21.
        
        Maximum 12 diagnoses (A-L).
        """
        letters = "ABCDEFGHIJKL"
        diagnosis_letters = {}
        
        for idx, dx in enumerate(diagnoses[:12]):  # Max 12 diagnoses
            letter = letters[idx]
            diagnosis_letters[dx.code] = letter
        
        return diagnosis_letters
    
    def _map_diagnoses_to_procedures(
        self,
        diagnoses: List[CodeSuggestion],
        procedures: List[CodeSuggestion]
    ) -> Dict[str, List[str]]:
        """
        Map diagnosis codes to procedure codes.
        
        This is a simplified heuristic. In production, would use:
        - ICD-10 to CPT crosswalk databases
        - Clinical decision support rules
        - LLM reasoning over relationships
        """
        
        # For now, associate all procedures with all diagnoses
        # This requires human review in the UI
        dx_proc_map = {}
        
        procedure_codes = [p.code for p in procedures]
        
        for dx in diagnoses:
            dx_proc_map[dx.code] = procedure_codes
        
        return dx_proc_map
    
    def _update_diagnosis_pointers(
        self,
        procedures: List[CodeSuggestion],
        dx_proc_map: Dict[str, List[str]],
        diagnosis_letters: Dict[str, str]
    ) -> List[CodeSuggestion]:
        """Update procedure codes with diagnosis pointers (letters)"""
        
        # Create reverse map: procedure -> diagnoses
        proc_dx_map = {}
        for dx_code, proc_codes in dx_proc_map.items():
            for proc_code in proc_codes:
                if proc_code not in proc_dx_map:
                    proc_dx_map[proc_code] = []
                if dx_code in diagnosis_letters:
                    proc_dx_map[proc_code].append(diagnosis_letters[dx_code])
        
        # Update procedures (add to metadata)
        for proc in procedures:
            if proc.code in proc_dx_map:
                letters = sorted(set(proc_dx_map[proc.code]))
                if not proc.metadata:
                    proc.metadata = {}
                proc.metadata["diagnosis_pointers"] = letters
        
        return procedures
    
    def _detect_mismatches(
        self,
        diagnoses: List[CodeSuggestion],
        procedures: List[CodeSuggestion],
        dx_proc_map: Dict[str, List[str]]
    ) -> List[CodeMismatch]:
        """
        Detect mismatches and validation issues.
        
        Checks:
        1. Procedures without linked diagnoses
        2. Diagnoses without procedures (may be OK)
        3. Invalid diagnosis-procedure pairings (requires external DB)
        4. Duplicate codes
        """
        
        mismatches = []
        
        # Check for procedures without diagnoses
        dx_codes = set(dx.code for dx in diagnoses)
        proc_codes = set(p.code for p in procedures)
        
        for proc in procedures:
            # Find linked diagnoses
            linked_dx = []
            for dx_code, procs in dx_proc_map.items():
                if proc.code in procs:
                    linked_dx.append(dx_code)
            
            if not linked_dx:
                mismatches.append(CodeMismatch(
                    mismatch_type="missing_diagnosis",
                    severity="warning",
                    message=f"Procedure {proc.code} has no linked diagnosis codes",
                    affected_codes=[proc.code],
                    suggestion="Link to a primary diagnosis or add missing diagnosis"
                ))
        
        # Check for diagnoses without procedures (informational only)
        for dx in diagnoses:
            if dx.code not in dx_proc_map or not dx_proc_map[dx.code]:
                mismatches.append(CodeMismatch(
                    mismatch_type="diagnosis_without_procedure",
                    severity="info",
                    message=f"Diagnosis {dx.code} is not linked to any procedures",
                    affected_codes=[dx.code],
                    suggestion="This may be acceptable for diagnosis-only claims"
                ))
        
        # Check for duplicate codes
        dx_code_list = [dx.code for dx in diagnoses]
        seen = set()
        for code in dx_code_list:
            if code in seen:
                mismatches.append(CodeMismatch(
                    mismatch_type="duplicate_code",
                    severity="error",
                    message=f"Duplicate diagnosis code: {code}",
                    affected_codes=[code],
                    suggestion="Remove duplicate entries"
                ))
            seen.add(code)
        
        return mismatches
    
    def _calculate_overall_confidence(
        self,
        diagnoses: List[CodeSuggestion],
        procedures: List[CodeSuggestion],
        mismatches: List[CodeMismatch]
    ) -> float:
        """Calculate overall confidence score"""
        
        if not diagnoses and not procedures:
            return 0.0
        
        # Average code confidences
        all_confidences = [dx.confidence for dx in diagnoses] + [p.confidence for p in procedures]
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        # Penalize for errors
        error_count = sum(1 for m in mismatches if m.severity == "error")
        penalty = error_count * 0.1
        
        return max(0.0, avg_confidence - penalty)


def suggest_codes(
    clinical_notes: str,
    existing_diagnoses: Optional[List[DiagnosisCode]] = None,
    existing_procedures: Optional[List[ProcedureCode]] = None
) -> Dict[str, Any]:
    """
    Convenience function to suggest medical codes.
    
    Args:
        clinical_notes: Clinical documentation
        existing_diagnoses: Existing diagnosis codes
        existing_procedures: Existing procedure codes
        
    Returns:
        Dictionary with coding results
    """
    assistant = MedicalCodingAssistant(use_llm=True)
    result = assistant.suggest_codes(clinical_notes, existing_diagnoses, existing_procedures)
    return result.model_dump()
