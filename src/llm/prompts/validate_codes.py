"""
Code Validation Prompt Template
Validates medical code pairings and detects potential errors.
"""

VALIDATION_PROMPT = """You are a medical coding validation specialist. Review the following diagnosis and procedure codes for accuracy and appropriate pairing.

Diagnoses:
{diagnoses}

Procedures:
{procedures}

Diagnosis-Procedure Mapping:
{mapping}

Analyze for:
1. Invalid or outdated codes
2. Inappropriate diagnosis-procedure pairings
3. Missing diagnoses for procedures
4. Specificity issues (e.g., unspecified codes when specific available)
5. Medical necessity concerns
6. Sequencing issues (primary vs secondary diagnoses)

Provide a JSON response:

{{
  "valid": true/false,
  "errors": [
    {{
      "type": "invalid_code|inappropriate_pairing|missing_dx|specificity|necessity|sequencing",
      "severity": "error|warning|info",
      "message": "Detailed explanation",
      "affected_codes": ["code1", "code2"],
      "suggestion": "How to fix"
    }}
  ],
  "overall_confidence": 0.0-1.0
}}

Return ONLY the JSON object."""
