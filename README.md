# MediVault AI Agent 🏥

**HIPAA-Aware Claims Automation Assistant for Healthcare**

MediVault AI Agent is an end-to-end, locally-hosted system that streamlines medical claims processing through intelligent OCR, data extraction, medical coding, and CMS-1500 form generation—all powered by Ollama's Llama models with HIPAA compliance built in.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HIPAA Aware](https://img.shields.io/badge/HIPAA-Aware-green.svg)](docs/compliance.md)

---

## ✨ Features

### 🔍 **Multi-Modal Document Ingestion**
- **OCR Engine:** Tesseract (primary) + Llama 3.2 Vision (fallback)
- **Format Support:** PDF, PNG, JPG, TXT
- **Confidence Scoring:** Identify low-quality extractions for manual review

### 🧠 **Intelligent Data Extraction**
- **Structured Extraction:** Patient demographics, insurance info, provider details
- **LLM-Enhanced:** Combine regex patterns with Ollama for robustness
- **Date Normalization:** Handle multiple date formats automatically

### 💊 **Medical Coding Assistant**
- **ICD-10 & CPT Mapping:** Suggest diagnosis and procedure codes from clinical notes
- **Rationale Generation:** Explain why each code was suggested
- **Validation:** Detect code mismatches and invalid pairings
- **Confidence Scores:** Flag low-confidence suggestions for provider review

### 📄 **CMS-1500 Form Generation**
- **NUCC Compliant:** All 33 items per CMS-1500 (02/12) specifications
- **Comprehensive Validation:** Required fields, format checks, medical necessity
- **Preview & Export:** Structured claim display + JSON export

### 🔒 **HIPAA Compliance**
- **Encryption at Rest:** Fernet (AES-128-CBC) for all PHI
- **Audit Logging:** Structured logs for all PHI operations (§164.312(b))
- **Access Controls:** Role-based authentication (Admin, Provider, Staff, ReadOnly)
- **Policy Enforcement:** Minimum necessary, consent management, Safe Harbor de-identification

### 💬 **Chat-Based Workflow UI**
- **Streamlit Interface:** Intuitive web app for claims processing
- **AI Assistant:** Context-aware chat powered by Ollama
- **Human-in-the-Loop:** Review, edit, and approve all extractions and codes

### 🏠 **Local-First Architecture**
- **No External APIs:** All processing happens on your hardware
- **Ollama Integration:** Run Llama 3.2 and Llama 3.2 Vision locally
- **Privacy by Design:** PHI never leaves your environment

---

## 🚀 Quick Start

> **New to the project?** See **[SETUP.md](SETUP.md)** for a comprehensive step-by-step setup guide!

### Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Ollama** (for local LLM)
   ```bash
   # Install from https://ollama.com/download
   ollama --version
   
   # Pull required models
   ollama pull llama3.2
   ollama pull llama3.2-vision
   ```

3. **Tesseract OCR**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Verify installation
   tesseract --version
   ```

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/your/projects
   git clone <repository-url>
   cd Medivault-AI-Agent
   ```

2. **Bootstrap the environment**
   ```bash
   make bootstrap
   # This will:
   # - Create Python virtual environment
   # - Install all dependencies
   # - Check Ollama and Tesseract
   # - Generate encryption keys
   # - Create necessary directories
   ```

3. **Configure environment**
   ```bash
   # Edit .env with your settings
   cp .env.example .env
   
   # IMPORTANT: Generate a strong encryption key
   # The bootstrap script does this automatically, but you can regenerate:
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

4. **Run the application**
   ```bash
   make run
   # Streamlit will start at http://localhost:8501
   ```

### First Use

1. **Login**
   - Default credentials: `admin` / `admin123`
   - ⚠️ **Change default password immediately in production!**

2. **Accept HIPAA Consent**
   - Review and accept consent dialog
   - Select purpose (Treatment, Payment, Operations, Research)

3. **Process a Document**
   - Upload a medical record (PDF, image, or text)
   - Review OCR results and extracted data
   - Accept or modify suggested medical codes
   - Generate and validate CMS-1500 claim
   - Export to JSON

---

## 📁 Project Structure

```
Medivault-AI-Agent/
├── src/
│   ├── app.py                    # Streamlit UI application
│   ├── core/
│   │   ├── ocr.py                # OCR engine (Tesseract + Llama Vision)
│   │   ├── parsing.py            # Document parser
│   │   ├── extraction.py         # Data extraction with LLM
│   │   └── coding.py             # Medical coding assistant
│   ├── llm/
│   │   ├── ollama.py             # Ollama client
│   │   └── prompts/              # LLM prompt templates
│   ├── cms1500/
│   │   ├── schema.py             # CMS-1500 data model
│   │   ├── rules.py              # Validation rules
│   │   ├── generator.py          # Claim generator
│   │   └── render.py             # Claim renderer
│   └── security/
│       ├── storage.py            # At-rest encryption
│       ├── audit.py              # Audit logging
│       ├── auth.py               # Authentication & RBAC
│       └── policy.py             # HIPAA policy enforcement
├── tests/
│   ├── test_cms1500_rules.py     # CMS-1500 validation tests
│   ├── test_extraction.py        # Data extraction tests
│   ├── test_coding.py            # Medical coding tests
│   └── conftest.py               # Pytest fixtures
├── scripts/
│   ├── bootstrap.sh              # First-time setup
│   ├── run_streamlit.sh          # Launch Streamlit
│   └── e2e_demo.sh               # End-to-end demo
├── docs/
│   ├── architecture.md           # System architecture
│   ├── compliance.md             # HIPAA compliance guide
│   ├── cms1500_reference.md      # CMS-1500 field reference
│   └── timeline.md               # Development timeline
├── Makefile                      # Build automation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## 🛠️ Usage

### Command-Line Interface

```bash
# Set up environment (first time only)
make bootstrap

# Install/update dependencies
make install

# Run the application
make run

# Run tests
make test

# Run tests with coverage
make coverage

# Lint code
make lint

# Check Ollama status
make check-ollama

# Clean environment
make clean
```

### Running E2E Demo

```bash
# Automated demo workflow
./scripts/e2e_demo.sh

# This will:
# 1. Check prerequisites
# 2. Start Streamlit
# 3. Guide you through sample claim workflow
```

### API Usage (Python)

```python
from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor
from src.core.coding import MedicalCodingAssistant
from src.cms1500.generator import CMS1500Generator
from src.cms1500.rules import CMS1500Validator

# 1. OCR
ocr = OCREngine()
ocr_result = ocr.process_document("path/to/medical_record.pdf")

# 2. Extract structured data
extractor = DataExtractor()
extracted = extractor.extract(ocr_result.full_text)

# 3. Suggest medical codes
coding = MedicalCodingAssistant()
coding_result = coding.suggest_codes(clinical_notes="Patient presents with...")

# 4. Generate CMS-1500 claim
generator = CMS1500Generator()
claim = generator.create_claim(extracted, coding_result)

# 5. Validate claim
validator = CMS1500Validator()
validation = validator.validate(claim)

if validation.is_valid:
    print("✅ Claim is valid!")
else:
    for error in validation.errors:
        print(f"❌ {error.message}")
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_cms1500_rules.py -v

# Run with coverage report
make coverage

# Run tests for specific module
pytest tests/test_extraction.py::test_extract_patient_name -v
```

### Test Coverage

Current coverage: **~80%** (target: >80%)

Key test areas:
- ✅ CMS-1500 validation rules
- ✅ Data extraction logic
- ✅ Medical coding suggestions
- ✅ Security modules (encryption, audit, auth)
- ⚠️ Integration tests (in progress)

---

## 🔐 Security & Compliance

### HIPAA Compliance

MediVault AI Agent implements technical safeguards per HIPAA Security Rule:

- **Administrative Safeguards (§164.308)**
  - Risk analysis and management
  - Workforce security and training
  - Incident response procedures
  - Contingency planning

- **Physical Safeguards (§164.310)**
  - Facility access controls (customer responsibility)
  - Workstation security (customer responsibility)
  - Device and media controls (encrypted storage)

- **Technical Safeguards (§164.312)**
  - ✅ Access control (§164.312(a)(2)(i)) - RBAC implemented
  - ✅ Audit controls (§164.312(b)) - All PHI operations logged
  - ✅ Integrity (§164.312(c)(1)) - Encryption prevents tampering
  - ✅ Authentication (§164.312(d)) - Password-based auth with PBKDF2
  - ✅ Transmission security (§164.312(e)(1)) - No network transmission (local-first)

**See [docs/compliance.md](docs/compliance.md) for complete details.**

### Customer Responsibilities

⚠️ **Important:** This software provides technical controls, but **you are responsible for:**

- [ ] Signing Business Associate Agreements (BAAs) with covered entities
- [ ] Physical security of servers/workstations
- [ ] Workforce training on HIPAA policies
- [ ] Regular risk assessments
- [ ] Backup and disaster recovery
- [ ] Incident response and breach notification
- [ ] Key management (consider AWS KMS, Azure Key Vault, or HashiCorp Vault)

### Security Best Practices

1. **Change default credentials immediately**
   ```python
   # Edit src/security/auth.py or implement external auth
   ```

2. **Use strong encryption keys**
   ```bash
   # Generate new key
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   # Add to .env
   echo "ENCRYPTION_KEY=<your-key>" >> .env
   ```

3. **Rotate keys regularly**
   ```bash
   # Quarterly key rotation recommended
   # See docs/compliance.md for procedures
   ```

4. **Monitor audit logs**
   ```bash
   # Review logs in logs/audit.log
   tail -f logs/audit.log | jq .
   ```

5. **Keep dependencies updated**
   ```bash
   # Check for security updates
   pip list --outdated
   # Update dependencies
   make install
   ```

---

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)** - System design, components, data flows
- **[HIPAA Compliance](docs/compliance.md)** - Security Rule implementation, customer responsibilities
- **[CMS-1500 Reference](docs/cms1500_reference.md)** - Field-by-field form guide with NUCC citations
- **[Development Timeline](docs/timeline.md)** - 8-week implementation roadmap

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Write tests** for new functionality
4. **Ensure all tests pass** (`make test`)
5. **Lint your code** (`make lint`)
6. **Commit changes** (`git commit -m 'Add amazing feature'`)
7. **Push to branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Code Standards

- **Style:** Black formatter, isort for imports
- **Linting:** Pylint (score >8.0)
- **Type Hints:** Required for all public functions
- **Docstrings:** Google-style docstrings
- **Testing:** Pytest with >80% coverage target

---

## 🐛 Troubleshooting

### Ollama Connection Errors

```bash
# Check Ollama service
ollama list

# Restart Ollama
ollama serve

# Pull models again
ollama pull llama3.2
ollama pull llama3.2-vision
```

### Tesseract Not Found

```bash
# Verify Tesseract installation
which tesseract

# Install if missing (macOS)
brew install tesseract

# Install if missing (Ubuntu)
sudo apt-get install tesseract-ocr
```

### Import Errors

```bash
# Reinstall dependencies
make clean
make venv
make install
```

### Permission Errors

```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix log directory permissions
mkdir -p logs data
chmod 700 logs data
```

### Low OCR Accuracy

1. **Improve image quality:** Scan at 300+ DPI, ensure good lighting
2. **Use Llama Vision fallback:** Set `use_vision=True` in OCR engine
3. **Manual review:** Use Streamlit UI to correct extractions

---

## 📊 Performance

### Typical Processing Times

| Task | Time (Standard Quality) | Time (Low Quality) |
|------|------------------------|-------------------|
| OCR (1-page PDF) | ~5-10 seconds | ~15-30 seconds |
| Data Extraction | ~2-5 seconds | ~5-10 seconds |
| Medical Coding | ~10-15 seconds | ~20-30 seconds |
| CMS-1500 Generation | <1 second | <1 second |
| **Total E2E** | **~20-30 seconds** | **~40-70 seconds** |

### Optimization Tips

1. **Use SSD storage** for faster file I/O
2. **Allocate sufficient RAM** (8GB+ recommended for Ollama)
3. **Batch process** multiple documents in parallel (future enhancement)
4. **Cache LLM responses** for repeated queries (future enhancement)

---

## 🗺️ Roadmap

### v1.1 (Planned)
- [ ] Docker containerization
- [ ] Support for UB-04 form (hospital claims)
- [ ] Integration with practice management systems (Epic, Cerner)
- [ ] Real-time eligibility verification

### v1.2 (Planned)
- [ ] Fine-tuned OCR model for medical documents
- [ ] Claims analytics dashboard
- [ ] Batch processing API
- [ ] Mobile app (iOS/Android)

### v2.0 (Future)
- [ ] Multi-language support (Spanish, Mandarin)
- [ ] Dental claims (ADA forms)
- [ ] Prior authorization automation
- [ ] Revenue cycle management integration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT:** This software is provided for **educational and research purposes only**.

- ❌ **NOT FDA-approved** for clinical use
- ❌ **NOT certified** for production healthcare environments
- ❌ **NOT a substitute** for professional medical coding or billing services

**Before using in production:**
1. Consult legal counsel regarding HIPAA compliance
2. Conduct thorough security and risk assessments
3. Obtain appropriate certifications and approvals
4. Implement comprehensive testing with real-world data
5. Establish incident response and disaster recovery plans
6. Execute Business Associate Agreements with covered entities

**Use at your own risk.** The authors and contributors assume no liability for any damages, losses, or regulatory violations arising from the use of this software.

---

## 🙏 Acknowledgments

- **NUCC (National Uniform Claim Committee)** for CMS-1500 specifications
- **CMS (Centers for Medicare & Medicaid Services)** for claims processing guidelines
- **Ollama** for local LLM infrastructure
- **Tesseract OCR** for open-source OCR engine
- **Streamlit** for rapid UI development
- **Python community** for excellent libraries (Pydantic, cryptography, pytest, etc.)

---

## 📧 Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/Medivault-AI-Agent/issues)
- **Security Vulnerabilities:** Please report privately to [security@example.com](mailto:security@example.com)
- **General Questions:** [Discussions](https://github.com/yourusername/Medivault-AI-Agent/discussions)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

**Built with ❤️ for healthcare professionals seeking to automate claims processing while maintaining HIPAA compliance.**

**MediVault AI Agent** - *Intelligent Claims Automation, Locally Hosted, HIPAA-Aware*