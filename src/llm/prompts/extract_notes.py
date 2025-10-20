"""
Data Extraction Prompt Template
Used to extract structured patient, insurance, provider, and medical data from documents.
"""

EXTRACTION_PROMPT = """You are a medical data extraction assistant. Extract structured information from the following medical document text.

Document Text:
{text}

Extract and return a JSON object with the following structure:

{{
  "patient": {{
    "first_name": "string or null",
    "middle_name": "string or null",
    "last_name": "string or null",
    "dob": "YYYY-MM-DD or null",
    "sex": "M/F/U or null",
    "address": "string or null",
    "city": "string or null",
    "state": "string or null",
    "zip_code": "string or null",
    "phone": "string or null"
  }},
  "insurance": {{
    "insurance_name": "string or null",
    "policy_number": "string or null",
    "group_number": "string or null",
    "subscriber_name": "string or null",
    "subscriber_relationship": "Self/Spouse/Child/Other or null"
  }},
  "provider": {{
    "provider_name": "string or null",
    "provider_npi": "string (10 digits) or null",
    "facility_name": "string or null",
    "facility_npi": "string (10 digits) or null",
    "tax_id": "string or null"
  }},
  "diagnoses": [
    {{
      "code": "ICD-10 code",
      "description": "diagnosis description",
      "confidence": 0.0-1.0
    }}
  ],
  "procedures": [
    {{
      "code": "CPT/HCPCS code",
      "description": "procedure description",
      "confidence": 0.0-1.0
    }}
  ]
}}

Guidelines:
- Extract only information explicitly present in the text
- Use null for missing fields
- Format dates as YYYY-MM-DD
- Validate ICD-10 codes (letter followed by 2 digits, optional decimal and more digits)
- Validate CPT codes (5 digits)
- Provide confidence scores based on clarity of source text
- Be conservative with medical codes - only extract if clearly stated

Return ONLY the JSON object, no additional text."""
