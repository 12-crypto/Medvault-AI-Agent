# MediVault AI Agent 🏥

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A HIPAA-compliant, local-first AI assistant for medical claims automation**

MediVault AI Agent is an intelligent medical document processing system that extracts patient data, suggests medical codes, generates CMS-1500 claim forms, and answers questions about medical records using local AI models. All processing happens on your machine—no data leaves your system.

---

## ✨ Features

### 🔍 **Intelligent Document Processing**
- **Multi-format Support**: Process PDFs, images (PNG, JPG), and text files
- **OCR Integration**: Extract text from scanned documents using Tesseract
- **Hybrid Extraction**: Combines rule-based patterns with LLM enhancement for accurate data extraction
- **Structured Data Extraction**: Automatically extracts:
  - Patient demographics (name, DOB, address, contact info)
  - Insurance information (policy numbers, group numbers, subscriber details)
  - Provider information (NPI, facility details, tax IDs)
  - Diagnosis codes (ICD-10)
  - Procedure codes (CPT/HCPCS)
  - Dates and financial amounts

### 🤖 **AI-Powered Medical Coding**
- **Intelligent Code Suggestions**: Uses local LLM (Ollama) to suggest appropriate medical codes
- **Code Validation**: Validates codes against medical coding rules
- **Confidence Scoring**: Provides confidence levels for each suggested code
- **Diagnosis-Procedure Mapping**: Automatically links procedures to diagnoses

### 📋 **CMS-1500 Claim Generation**
- **Automated Form Filling**: Generates complete CMS-1500 (02/12) claim forms
- **PDF Export**: Download professionally formatted PDF forms ready for submission
- **JSON Export**: Export claim data in structured JSON format
- **Form Validation**: Validates claims against NUCC specifications
- **Proper Alignment**: Text is correctly aligned within form fields

### 💬 **AI Chat Assistant**
- **Context-Aware Q&A**: Ask questions about extracted medical data
- **Intelligent Responses**: Answers based on patient info, diagnoses, procedures, charges, and dates
- **Conversation History**: Maintains context across multiple questions
- **No External APIs**: All AI processing happens locally using Ollama

### 🔒 **Security & Compliance**
- **HIPAA-Aware**: Built with HIPAA compliance in mind
- **Local Processing**: All data stays on your machine
- **Encrypted Storage**: Patient data encrypted at rest
- **Audit Logging**: Comprehensive audit trail of all actions
- **Access Control**: Role-based authentication system
- **Consent Management**: Tracks user consent for PHI processing

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** (for local AI models)
- **Tesseract OCR** (for PDF/image text extraction)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/12-crypto/Medvault-AI-Agent.git
   cd Medvault-AI-Agent
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama models:**
   ```bash
   ollama pull llama3.2
   ```

5. **Set up environment:**
   ```bash
   # Generate encryption key
   python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" > .env
   echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
   ```

6. **Create required directories:**
   ```bash
   mkdir -p logs data uploads
   chmod 700 logs data uploads
   ```

7. **Run the application:**
   ```bash
   streamlit run src/app.py
   ```

8. **Access the app:**
   - Open http://localhost:8501 in your browser
   - Login with: `admin` / `admin123` (⚠️ change in production!)

For detailed setup instructions, see [SETUP.md](SETUP.md).

---

## 📖 Usage Guide

### 1. **Upload Medical Document**

- Click "Browse files" in the Document Upload section
- Select a PDF, image, or text file containing medical information
- Click "Process Document"

The system will:
- Extract text using OCR (if needed)
- Parse the document structure
- Extract patient, insurance, provider, diagnoses, and procedures

### 2. **Review Extracted Data**

View extracted information in organized tabs:
- **Patient Info**: Demographics, contact information
- **Insurance**: Policy details, subscriber information
- **Provider**: NPI, facility details
- **Diagnoses**: ICD-10 codes with descriptions
- **Procedures**: CPT/HCPCS codes with charges

### 3. **Medical Coding**

The system automatically:
- Suggests appropriate medical codes
- Validates code accuracy
- Maps procedures to diagnoses
- Provides confidence scores

### 4. **Generate CMS-1500 Claim**

- Click "Generate CMS-1500 Claim"
- Review the generated claim in the preview tabs
- **Download PDF**: Get a professionally formatted PDF form
- **Download JSON**: Export structured data for integration

### 5. **Ask Questions**

Use the AI Assistant chat to ask questions like:
- "What is the total charge?"
- "What diagnoses were found?"
- "What procedures were performed?"
- "What is the patient's date of birth?"

The AI answers based on the extracted medical data.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit Web Interface (app.py)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Document     │  │ Chat         │  │ CMS-1500     │ │
│  │ Processing   │  │ Assistant    │  │ Generation   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Core Modules │ │ LLM (Ollama) │ │ Security     │
│              │ │              │ │              │
│ • OCR        │ │ • Chat       │ │ • Auth       │
│ • Parsing    │ │ • Extraction │ │ • Audit      │
│ • Extraction │ │ • Coding     │ │ • Storage    │
│ • Coding     │ │ • Q&A        │ │ • Policy     │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │
        └───────┬───────┘
                ▼
        ┌──────────────┐
        │ CMS-1500     │
        │ Generator    │
        │ & PDF Export │
        └──────────────┘
```

### Key Components

- **`src/core/`**: Core processing modules (OCR, parsing, extraction, coding)
- **`src/llm/`**: LLM integration with Ollama (chat, extraction, Q&A)
- **`src/cms1500/`**: CMS-1500 form generation and PDF export
- **`src/security/`**: Authentication, audit logging, encryption
- **`src/app.py`**: Main Streamlit application

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

---

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Required: Encryption key for PHI
ENCRYPTION_KEY=your_encryption_key_here

# Required: Ollama API endpoint
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Custom Ollama models
OLLAMA_MODEL=llama3.2
OLLAMA_VISION_MODEL=llama3.2-vision

# Optional: Logging level
LOG_LEVEL=INFO
```

### Makefile Commands

```bash
make install      # Install dependencies
make run          # Run the application
make test         # Run tests
make lint         # Lint code
make check-ollama # Check Ollama status
make bootstrap    # First-time setup
```

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_extraction.py -v
```

See [TESTING.md](TESTING.md) for comprehensive testing guide.

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)**: Detailed installation and setup guide
- **[TESTING.md](TESTING.md)**: Testing guide and examples
- **[QUICK_TEST.md](QUICK_TEST.md)**: Quick start guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**: Daily reference card
- **[docs/architecture.md](docs/architecture.md)**: System architecture
- **[docs/compliance.md](docs/compliance.md)**: HIPAA compliance guide
- **[docs/cms1500_reference.md](docs/cms1500_reference.md)**: CMS-1500 form reference

---

## 🔒 Security & Compliance

### HIPAA Compliance Features

- ✅ **Local Processing**: No data sent to external servers
- ✅ **Encryption**: Data encrypted at rest using Fernet
- ✅ **Access Control**: Role-based authentication
- ✅ **Audit Logging**: Comprehensive audit trail
- ✅ **Consent Management**: Tracks user consent for PHI processing
- ✅ **Data Minimization**: Only processes necessary data

### Security Checklist

Before using with real patient data:

- [ ] Change default admin credentials
- [ ] Generate new encryption key
- [ ] Set up proper key management (KMS)
- [ ] Review HIPAA compliance requirements
- [ ] Configure audit logging
- [ ] Set directory permissions (700)
- [ ] Train users on HIPAA policies
- [ ] Execute Business Associate Agreements

See [docs/compliance.md](docs/compliance.md) for detailed compliance information.

---

## 🛠️ Development

### Project Structure

```
Medvault-AI-Agent/
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── core/               # Core processing modules
│   │   ├── extraction.py   # Data extraction
│   │   ├── coding.py       # Medical coding
│   │   ├── parsing.py      # Document parsing
│   │   └── ocr.py          # OCR integration
│   ├── llm/                # LLM integration
│   │   ├── ollama.py       # Ollama client
│   │   └── prompts/        # Prompt templates
│   ├── cms1500/            # CMS-1500 form generation
│   │   ├── generator.py    # Claim generator
│   │   ├── pdf_generator.py # PDF form generator
│   │   ├── schema.py       # Form schema
│   │   └── rules.py        # Validation rules
│   └── security/           # Security modules
│       ├── auth.py         # Authentication
│       ├── audit.py        # Audit logging
│       └── storage.py     # Encrypted storage
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Adding New Features

1. **New Extraction Field**: Add to `src/core/extraction.py`
2. **New LLM Prompt**: Add to `src/llm/prompts/`
3. **New Form Field**: Update `src/cms1500/schema.py`
4. **New Test**: Add to `tests/`

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Write tests for new features
- Run `black` and `flake8` before committing

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT**: This software is for educational and research purposes only. It is:

- ❌ NOT FDA-approved
- ❌ NOT certified for production healthcare environments
- ❌ NOT a substitute for professional medical coding or billing services

**Before using with real patient data:**
- Consult legal counsel
- Review HIPAA compliance requirements
- Obtain necessary certifications
- Execute Business Associate Agreements
- Use at your own risk

---

## 🙏 Acknowledgments

- **Ollama** for providing local LLM runtime
- **Streamlit** for the web framework
- **Tesseract OCR** for text extraction
- **NUCC** for CMS-1500 form specifications

---

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/12-crypto/Medvault-AI-Agent/issues)
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🎯 Roadmap

- [ ] Support for additional claim forms (UB-04, etc.)
- [ ] Integration with EHR systems
- [ ] Batch processing capabilities
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Enhanced OCR accuracy
- [ ] Real-time collaboration features

---

**Made with ❤️ for healthcare professionals**

*Last Updated: November 2024*
