"""
Medical Code Mapping Prompt Template
Maps clinical notes to ICD-10 and CPT/HCPCS codes with rationales.
"""

CODE_MAPPING_PROMPT = """You are an expert medical coding assistant. Analyze the following clinical notes and suggest appropriate ICD-10 diagnosis codes and CPT/HCPCS procedure codes.

Clinical Notes:
{clinical_notes}

Provide a JSON response with suggested codes, descriptions, and rationales:

{{
  "diagnoses": [
    {{
      "code": "ICD-10 code (e.g., J20.9, E11.9)",
      "description": "Full diagnosis description",
      "rationale": "Explanation of why this code applies based on the notes",
      "confidence": 0.0-1.0
    }}
  ],
  "procedures": [
    {{
      "code": "CPT or HCPCS code (e.g., 99213, 80053)",
      "description": "Full procedure description",
      "rationale": "Explanation of why this code applies",
      "confidence": 0.0-1.0
    }}
  ]
}}

Guidelines:
- Use standard ICD-10-CM codes (current version)
- Use CPT codes for procedures (5 digits) or HCPCS Level II (alphanumeric)
- Provide specific codes when possible; use unspecified (.9) only when details are unclear
- Include primary diagnosis and all relevant secondary diagnoses
- Include all procedures/services mentioned or implied
- Confidence should reflect specificity and clarity in the notes
- Always include rationale linking the note content to the code

Return ONLY the JSON object."""
