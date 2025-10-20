# MediVault AI Agent - Architecture

## Overview

MediVault AI Agent is a local-first, HIPAA-aware claims automation assistant that streamlines the entire workflow from document ingestion to CMS-1500 generation.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Document     │  │ Chat         │  │ CMS-1500        │  │
│  │ Upload       │  │ Assistant    │  │ Preview         │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│   Core       │     │   LLM Layer    │     │   Security   │
│   Modules    │     │   (Ollama)     │     │   Layer      │
│              │     │                │     │              │
│ • OCR        │────▶│ • Chat         │────▶│ • Storage    │
│ • Parsing    │     │ • Structured   │     │ • Audit      │
│ • Extraction │     │   Extraction   │     │ • Auth       │
│ • Coding     │     │ • Vision       │     │ • Policy     │
└──────────────┘     └────────────────┘     └──────────────┘
        │                     │
        └─────────┬───────────┘
                  ▼
        ┌────────────────────┐
        │   CMS-1500 Layer   │
        │                    │
        │ • Schema           │
        │ • Rules            │
        │ • Generator        │
        │ • Renderer         │
        └────────────────────┘
```

## Components

### 1. User Interface (`src/app.py`)
- **Streamlit-based** web interface
- **Features:**
  - Document upload (PDF, images, text)
  - Real-time chat assistant
  - Extracted data display
  - Medical code suggestions with rationale
  - CMS-1500 form preview
  - Validation messages with field-level errors
  - Export functionality (JSON)

### 2. Core Processing Layer

#### OCR Engine (`src/core/ocr.py`)
- **Primary:** Tesseract OCR for text extraction
- **Fallback:** Llama 3.2 Vision for low-quality scans
- **Output:** DocumentBlocks with text, confidence, bounding boxes

#### Parser (`src/core/parsing.py`)
- Handles PDF (text + scanned), images, plain text
- Uses pdfplumber (preferred) and PyPDF2 (fallback)
- Text cleaning and normalization

#### Data Extractor (`src/core/extraction.py`)
- **Rule-based:** Regex patterns for structured fields
- **LLM-enhanced:** Ollama for complex/unstructured data
- **Extracts:**
  - Patient demographics
  - Insurance information
  - Provider/facility details
  - Preliminary ICD-10/CPT codes

#### Medical Coding Assistant (`src/core/coding.py`)
- Maps clinical notes to ICD-10 and CPT/HCPCS
- Assigns diagnosis letters (A-L) for CMS-1500
- Maps diagnoses to procedures
- Detects mismatches and validation issues
- Provides confidence scores and rationales

### 3. CMS-1500 Layer

#### Schema (`src/cms1500/schema.py`)
- **Pydantic models** for type safety
- All 33 numbered items per NUCC 1500 v02/12
- ServiceLineInfo for Item 24 (up to 6 lines)
- Field-level validators

#### Rules Engine (`src/cms1500/rules.py`)
- Implements NUCC and Medicare specifications
- Validates:
  - Required fields
  - Format (NPI, dates, codes)
  - Business rules (diagnosis pointers, charge calculations)
  - Cross-field logic
- Returns structured ValidationResult with severity levels

#### Generator (`src/cms1500/generator.py`)
- Maps extracted data → CMS-1500 fields
- Handles date format conversions
- Calculates totals
- Applies NUCC field mapping rules

#### Renderer (`src/cms1500/render.py`)
- Formats claim for UI display
- Organizes by sections (patient, insurance, diagnoses, services)
- Prepares for export

### 4. LLM Integration Layer

#### Ollama Client (`src/llm/ollama.py`)
- Communicates with local Ollama service
- **Capabilities:**
  - Chat completions
  - Structured JSON extraction
  - Vision analysis (images)
  - Streaming support
- **Models:** llama3.2, llama3.2-vision

#### Prompt Templates (`src/llm/prompts/`)
- `extract_notes.py`: Structured data extraction
- `code_mapping.py`: ICD-10/CPT suggestion
- `validate_codes.py`: Code validation and cross-checking

### 5. Security & Compliance Layer

#### Secure Storage (`src/security/storage.py`)
- **At-rest encryption:** Fernet (AES-128-CBC)
- **Key management:** Environment-based or password-derived (PBKDF2)
- **PHI storage:** Encrypted files with restricted permissions
- **HIPAA:** 164.312(a)(2)(iv), 164.312(e)(2)(ii)

#### Audit Logger (`src/security/audit.py`)
- **Structured JSON logs** with timestamp, user, resource, action
- **Events:** access, create, update, delete, login, consent
- **HIPAA:** 164.312(b), 164.308(a)(1)(ii)(D)

#### Auth Manager (`src/security/auth.py`)
- **Simple RBAC** for local deployment
- Roles: admin, provider, staff, readonly
- Password hashing: PBKDF2-SHA256
- **HIPAA:** 164.312(a)(2)(i), 164.312(d)

#### Policy Manager (`src/security/policy.py`)
- **Minimum Necessary Rule:** Field filtering by purpose
- **PHI Redaction:** Safe Harbor method for LLM calls
- **Consent Management:** Per-patient, per-purpose tracking
- **Data Retention:** Configurable (default 90 days)
- **HIPAA:** 164.502(b), 164.514(d)

## Data Flow

### Document Processing Flow
```
1. User uploads document
   ↓
2. Consent check (HIPAA requirement)
   ↓
3. Parse document (PDF/image → text)
   ↓
4. OCR if needed (Tesseract + optional Vision)
   ↓
5. Extract structured data (regex + LLM)
   ↓
6. Medical coding assistant (ICD-10, CPT)
   ↓
7. Generate CMS-1500 claim
   ↓
8. Validate claim (NUCC/CMS rules)
   ↓
9. Display for review + export
   ↓
10. Audit log all operations
```

### Security Flow
```
User Action → Authentication → Authorization → 
  PHI Minimization → Processing → 
  Encryption (at rest) → Audit Log
```

## Technology Stack

- **Python 3.10+**
- **UI:** Streamlit 1.32
- **LLM:** Ollama (llama3.2, llama3.2-vision)
- **OCR:** Tesseract (pytesseract), Llama Vision
- **PDF:** PyPDF2, pdfplumber, pdf2image
- **Validation:** Pydantic 2.x
- **Security:** cryptography (Fernet), PBKDF2
- **Testing:** pytest

## Deployment Model

### Local-First Design
- **No external APIs** (no OpenAI, no cloud services)
- **All processing on-premise**
- **Data never leaves the machine**
- **Ollama runs locally** (CPU or GPU)

### Hardware Requirements
- **Minimum:** 8GB RAM, 4-core CPU
- **Recommended:** 16GB RAM, 8-core CPU, NVIDIA GPU (for faster LLM)
- **Storage:** 10GB for models + data

### Network
- **Default:** Localhost only (127.0.0.1:8501)
- **Optional TLS:** For LAN deployment
- **No analytics/tracking** (HIPAA compliant)

## Extensibility

### Plugin Points
1. **OCR Engines:** Add custom OCR backends
2. **LLM Providers:** Swap Ollama for other local LLMs
3. **Validation Rules:** Extend CMS-1500 validators
4. **Export Formats:** Add 837P, FHIR, custom formats
5. **Auth Backends:** Integrate LDAP, SAML, OAuth

### Integration Targets
- **EHR Systems:** HL7 FHIR, CDA
- **Practice Management:** APIs for claim submission
- **Code Databases:** Link to authoritative ICD-10/CPT sources
- **Payer APIs:** Direct claim submission (requires BAA)

## Security Considerations

### Threat Model
- **In Scope:** Unauthorized PHI access, data breaches, audit gaps
- **Mitigations:** Encryption, access controls, audit logs, consent
- **Out of Scope:** Physical security, network security (customer responsibility)

### HIPAA Requirements Addressed
- ✅ **Unique User ID** (164.312(a)(2)(i))
- ✅ **Emergency Access** (164.312(a)(2)(ii)) - via admin role
- ✅ **Automatic Logoff** (164.312(a)(2)(iii)) - configurable session timeout
- ✅ **Encryption** (164.312(a)(2)(iv), 164.312(e)(2)(ii))
- ✅ **Audit Controls** (164.312(b))
- ✅ **Authentication** (164.312(d))

### Future Enhancements
- Two-factor authentication (2FA)
- Role-based data masking
- Automated PHI retention/deletion
- SIEM integration
- Advanced anomaly detection

## Performance

### Expected Throughput
- **OCR:** 1-2 pages/second (Tesseract)
- **Extraction:** 2-5 seconds per document
- **LLM Coding:** 5-10 seconds per note (Ollama)
- **Validation:** < 1 second per claim

### Optimization Opportunities
- **Batch processing** for multiple documents
- **GPU acceleration** for Ollama
- **Caching** for repeated queries
- **Async processing** for large documents

## Maintenance

### Logging
- **Application logs:** `logs/app.log`
- **Audit logs:** `logs/audit.log`
- **Error tracking:** Structured logging with context

### Monitoring
- Ollama service health
- Document processing success rates
- Validation error frequencies
- User activity patterns

### Updates
- **Models:** `ollama pull llama3.2`
- **Dependencies:** `pip install --upgrade -r requirements.txt`
- **Code:** Git pull + restart Streamlit
