"""
Medical Coding Assistant Module
LLM-powered mapping of clinical notes to ICD-10 and CPT/HCPCS codes
with cross-referencing and mismatch detection.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from core.extraction import DiagnosisCode, ProcedureCode

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
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Additional metadata (e.g., diagnosis pointers)


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
        , extraction_confidence: Optional[float] = None
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
        
        # Merge with existing codes (dedupe & prefer extracted source when possible)
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
        confidence = self._calculate_overall_confidence(all_diagnoses, all_procedures, mismatches, extraction_confidence)
        
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
        
        from llm.ollama import OllamaClient
        from llm.prompts.code_mapping import CODE_MAPPING_PROMPT
        
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
        # Deduplicate existing diagnoses by code, keeping the best (highest confidence)
        merged_map: Dict[str, CodeSuggestion] = {}

        for dx in existing:
            code = dx.code
            # Determine rationale from source_span or description
            if getattr(dx, 'source_span', None):
                rationale_text = f"Found in source: {dx.source_span}"
            elif getattr(dx, 'description', None):
                rationale_text = dx.description
            else:
                rationale_text = "Extracted from document"

            new_sugg = CodeSuggestion(
                code=code,
                code_type="ICD-10",
                description=dx.description or "",
                rationale=rationale_text,
                confidence=dx.confidence,
                source_text=dx.source_span
            )

            # If duplicate exists, keep the one with higher confidence or with description
            if code in merged_map:
                existing_sugg = merged_map[code]
                # Prefer higher confidence, or prefer one that has a description/source_text
                if new_sugg.confidence > existing_sugg.confidence:
                    merged_map[code] = new_sugg
                elif (existing_sugg.description == "" and new_sugg.description):
                    merged_map[code] = new_sugg
                # otherwise keep existing
            else:
                merged_map[code] = new_sugg

        # Add LLM suggestions only if code not present (or if they provide richer description)
        for suggestion in llm_suggestions:
            code = suggestion.code
            if code in merged_map:
                # If LLM suggestion has higher confidence or provides a description, merge fields
                existing_sugg = merged_map[code]
                if suggestion.confidence > existing_sugg.confidence:
                    # Update confidence and rationale if suggestion is stronger
                    existing_sugg.confidence = suggestion.confidence
                    if suggestion.description:
                        existing_sugg.description = suggestion.description
                    if suggestion.rationale:
                        existing_sugg.rationale = suggestion.rationale
                elif not existing_sugg.description and suggestion.description:
                    existing_sugg.description = suggestion.description
                # Keep source_text from extraction when available
            else:
                # Only include higher-confidence LLM suggestions to avoid false positives
                if suggestion.confidence >= 0.6:
                    merged_map[code] = suggestion

        # Preserve insertion order: prefer extracted order first, then LLM extras
        merged_list: List[CodeSuggestion] = []
        for dx in existing:
            if dx.code in merged_map:
                merged_list.append(merged_map.pop(dx.code))

        # Append remaining LLM-only suggestions
        for s in merged_map.values():
            merged_list.append(s)

        return merged_list
    
    def _merge_procedure_suggestions(
        self,
        existing: List[ProcedureCode],
        llm_suggestions: List[CodeSuggestion]
    ) -> List[CodeSuggestion]:
        """Merge existing procedure codes with LLM suggestions"""
        merged = []
        seen_codes = set()

        # If we have extracted procedures, prefer them and do not inject LLM suggestions
        # (which may not be present in the source document) to avoid showing extra codes
        for proc in existing:
            code_key = f"{proc.code}-{proc.modifier}" if proc.modifier else proc.code

            # Propagate extracted charge and service metadata into suggestion metadata
            metadata = {}
            if getattr(proc, 'charge', None) is not None:
                metadata['charge'] = proc.charge
            if getattr(proc, 'date_of_service', None):
                metadata['date_of_service'] = proc.date_of_service
            if getattr(proc, 'place_of_service', None):
                metadata['place_of_service'] = proc.place_of_service
            if getattr(proc, 'modifier', None):
                metadata['modifier'] = proc.modifier
            if getattr(proc, 'diagnosis_pointers', None):
                # propagate any explicit diagnosis pointers from extraction
                metadata['diagnosis_pointers'] = proc.diagnosis_pointers

            # Append extracted procedure (use code_key so modifiers are preserved)
            merged.append(CodeSuggestion(
                code=code_key,
                code_type="CPT" if len(proc.code) == 5 else "HCPCS",
                description=proc.description or "",
                rationale="Extracted from document",
                confidence=proc.confidence,
                metadata=metadata
            ))

            # Track both plain code and code+modifier to avoid duplicates from LLM
            seen_codes.add(proc.code)
            seen_codes.add(code_key)

        # If no extracted procedures present, fall back to LLM suggestions
        if not merged and llm_suggestions:
            for suggestion in llm_suggestions:
                # Only include high-confidence LLM suggestions to reduce false positives
                if suggestion.code not in seen_codes and suggestion.confidence >= 0.6:
                    merged.append(suggestion)
                    seen_codes.add(suggestion.code)

        # Final deduplication by code (prefer earlier entries)
        unique = []
        seen = set()
        for s in merged:
            base_code = s.code.split('-')[0]
            if base_code not in seen:
                unique.append(s)
                seen.add(base_code)

        return unique
    
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
        
        # Map procedures to diagnoses conservatively:
        # - If a procedure has explicit `diagnosis_pointers` metadata (letters A-L),
        #   map it only to those diagnoses.
        # - Otherwise, map the procedure to the primary diagnosis (first one),
        #   instead of mapping every procedure to every diagnosis.
        dx_proc_map = {dx.code: [] for dx in diagnoses}

        # Build local diagnosis letter map (A-L)
        letters = "ABCDEFGHIJKL"
        diagnosis_letter_map = {}
        for idx, dx in enumerate(diagnoses[:12]):
            diagnosis_letter_map[letters[idx]] = dx.code

        for proc in procedures:
            proc_code = proc.code
            pointers = []
            if proc.metadata and 'diagnosis_pointers' in proc.metadata:
                # Expect a list like ['A','B'] or a string; normalize to list
                ptr = proc.metadata.get('diagnosis_pointers')
                if isinstance(ptr, str):
                    pointers = list(ptr)
                elif isinstance(ptr, (list, tuple)):
                    pointers = list(ptr)

            if pointers:
                for letter in pointers:
                    dx_code = diagnosis_letter_map.get(letter)
                    if dx_code:
                        dx_proc_map.setdefault(dx_code, []).append(proc_code)
            else:
                # Conservative default: map to the first diagnosis only
                if diagnoses:
                    primary_dx = diagnoses[0].code
                    dx_proc_map.setdefault(primary_dx, []).append(proc_code)

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
        , extraction_confidence: Optional[float] = None
    ) -> float:
        """Calculate overall confidence score"""
        if not diagnoses and not procedures:
            return 0.0

        # Average confidence for diagnoses and procedures
        def avg_conf(items):
            if not items:
                return 0.0
            return sum(getattr(i, 'confidence', 0.0) for i in items) / len(items)

        dx_conf = avg_conf(diagnoses)
        proc_conf = avg_conf(procedures)

        # Weighted average: diagnoses carry slightly more weight
        base_score = 0.6 * dx_conf + 0.3 * proc_conf

        # If extractor provides an overall extraction confidence, factor it in
        if extraction_confidence is not None:
            # Blend extraction confidence modestly (10% weight)
            base_score = 0.9 * base_score + 0.1 * extraction_confidence

        # Penalize mismatches: errors penalize more than warnings
        penalty = 0.0
        for m in mismatches:
            if m.severity == 'error':
                penalty += 0.15
            elif m.severity == 'warning':
                penalty += 0.05
            # info => no penalty

        # Cap penalty to avoid negative scores
        penalty = min(penalty, 0.4)

        score = max(0.0, min(1.0, base_score - penalty))

        return score


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
    # No extraction_confidence available in this convenience wrapper
    result = assistant.suggest_codes(clinical_notes, existing_diagnoses, existing_procedures)
    return result.model_dump()
