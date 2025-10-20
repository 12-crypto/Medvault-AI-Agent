# MediVault AI Agent - Complete Setup Guide

**A step-by-step guide to get MediVault AI Agent running on your machine**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [First Run](#first-run)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

Before starting, ensure you have these installed:

#### 1. **Python 3.10 or Higher**

**Check if installed:**
```bash
python3 --version
```

**Expected output:** `Python 3.10.x` or higher

**If not installed:**

- **macOS:**
  ```bash
  brew install python@3.10
  ```

- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install python3.10 python3.10-venv python3-pip
  ```

- **Windows:**
  Download from https://www.python.org/downloads/

---

#### 2. **Ollama (Local LLM Runtime)**

Ollama runs the AI models locally without sending data to external servers.

**Check if installed:**
```bash
ollama --version
```

**If not installed:**

- **macOS/Linux:**
  Visit https://ollama.com/download and follow instructions
  
  Or use:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- **Windows:**
  Download installer from https://ollama.com/download

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

If you get a connection error, start Ollama:
```bash
ollama serve
```

---

#### 3. **Tesseract OCR**

Tesseract extracts text from PDF images and scanned documents.

**Check if installed:**
```bash
tesseract --version
```

**Expected output:** `tesseract 4.x.x` or `5.x.x`

**If not installed:**

- **macOS:**
  ```bash
  brew install tesseract
  ```

- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install tesseract-ocr
  ```

- **Windows:**
  Download installer from https://github.com/UB-Mannheim/tesseract/wiki

**Verify installation:**
```bash
which tesseract  # Should show path like /usr/local/bin/tesseract
```

---

#### 4. **Git (Optional but Recommended)**

**Check if installed:**
```bash
git --version
```

**If not installed:**

- **macOS:**
  ```bash
  xcode-select --install
  ```

- **Ubuntu/Debian:**
  ```bash
  sudo apt install git
  ```

- **Windows:**
  Download from https://git-scm.com/downloads

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS 10.15+, Ubuntu 20.04+, Windows 10+ |
| **CPU** | 2 cores, 2.0 GHz |
| **RAM** | 8 GB (16 GB recommended for LLM) |
| **Disk Space** | 10 GB free |
| **Python** | 3.10+ |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **CPU** | 4+ cores, 3.0+ GHz |
| **RAM** | 16 GB+ |
| **Disk** | 20 GB+ free (SSD preferred) |
| **GPU** | Optional (speeds up Ollama) |

---

## Installation Steps

### Step 1: Download/Clone the Project

**Option A: Clone with Git (Recommended)**
```bash
cd ~/Desktop  # or your preferred location
git clone https://github.com/12-crypto/Medvault-AI-Agent.git
cd Medvault-AI-Agent
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to a location like `~/Desktop/Medvault-AI-Agent`
3. Open terminal and navigate:
   ```bash
   cd ~/Desktop/Medvault-AI-Agent
   ```

---

### Step 2: Create Python Virtual Environment

A virtual environment keeps dependencies isolated from your system Python.

```bash
# Make sure you're in the project directory
cd ~/Desktop/Medvault-AI-Agent

# Create virtual environment
python3 -m venv venv

# Verify creation
ls -la venv/  # Should show bin/, lib/, etc.
```

---

### Step 3: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

**Verify activation:**
You should see `(venv)` at the start of your terminal prompt:
```
(venv) user@machine Medvault-AI-Agent %
```

---

### Step 4: Upgrade pip and Install Build Tools

```bash
pip install --upgrade pip setuptools wheel
```

**Expected output:**
```
Successfully installed pip-25.x setuptools-80.x wheel-0.x
```

---

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**This will install (~30 packages):**
- streamlit (UI framework)
- pydantic (data validation)
- cryptography (encryption)
- ollama (LLM client)
- pytesseract (OCR wrapper)
- PyPDF2, pdfplumber (PDF processing)
- pdf2image, Pillow (image handling)
- pytest (testing)
- And more...

**Expected duration:** 2-5 minutes depending on your internet speed

**Verify installation:**
```bash
pip list | grep -E "streamlit|pydantic|ollama"
```

Should show:
```
ollama          0.6.0
pydantic        2.12.3
streamlit       1.50.0
```

---

### Step 6: Install Ollama Models

Download the required AI models:

```bash
# Required model (2 GB)
ollama pull llama3.2
```

**Expected output:**
```
pulling manifest
pulling model...
████████████████████████ 100%
success
```

**Optional: Vision model for better OCR (4-7 GB)**
```bash
ollama pull llama3.2-vision
```

**Verify models:**
```bash
ollama list
```

Should show:
```
NAME               ID              SIZE      MODIFIED
llama3.2:latest    a80c4f17acd5    2.0 GB    X minutes ago
```

---

### Step 7: Create Environment Configuration

Create a `.env` file with encryption keys and settings:

```bash
# Generate encryption key and create .env file
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())" > .env

# Add Ollama URL
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env

# View the file
cat .env
```

**Expected `.env` contents:**
```
ENCRYPTION_KEY=f2Cvtd5bYIlC9Bs6_dm1wbcF5CJbFMp26wyIpvb9TVA=
OLLAMA_BASE_URL=http://localhost:11434
```

⚠️ **Important:** Keep this key secure! It encrypts all patient data.

---

### Step 8: Create Required Directories

```bash
# Create directories with secure permissions
mkdir -p logs data uploads
chmod 700 logs data uploads

# Verify
ls -ld logs data uploads
```

**Expected output:**
```
drwx------  logs
drwx------  data
drwx------  uploads
```

The `700` permissions mean only you (the owner) can read/write/execute.

---

### Step 9: Run Tests (Optional but Recommended)

Verify everything is working:

```bash
# Run unit tests
pytest tests/ -v

# Expected: 16/19 tests passing
```

**If tests fail:** See [Troubleshooting](#troubleshooting) section below.

---

## Configuration

### Environment Variables (.env)

Edit `.env` to customize settings:

```bash
nano .env  # or use your preferred editor
```

**Available settings:**

```bash
# Required: Encryption key for PHI (auto-generated)
ENCRYPTION_KEY=your_key_here

# Required: Ollama API endpoint
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Ollama models to use
OLLAMA_MODEL=llama3.2
OLLAMA_VISION_MODEL=llama3.2-vision

# Optional: Logging level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Optional: Custom data directories
DATA_DIR=./data
LOGS_DIR=./logs
UPLOADS_DIR=./uploads
```

---

### Makefile Commands

The project includes a `Makefile` for common tasks:

```bash
# Install dependencies
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

# Bootstrap (first-time setup)
make bootstrap
```

---

## First Run

### Start the Application

**Option 1: Using Makefile (Recommended)**
```bash
make run
```

**Option 2: Direct Command**
```bash
streamlit run src/app.py
```

**Option 3: Custom Port**
```bash
streamlit run src/app.py --server.port 8501 --server.address localhost
```

---

### Access the Application

**Expected terminal output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Open in browser:**
- Click the URL in terminal, or
- Manually navigate to http://localhost:8501

---

### Login

**Default credentials:**
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **IMPORTANT:** Change these credentials immediately in production!

To change credentials, edit `src/security/auth.py` or implement external authentication.

---

### Accept HIPAA Consent

On first use, you'll see a consent dialog:

1. **Review** the HIPAA disclosure
2. **Select purpose:** Treatment, Payment, Operations, or Research
3. **Click** "I Accept"

This consent is logged in `logs/audit.log` for compliance.

---

### Upload Your First Document

**Use the sample file:**

```bash
# Create a sample medical record
python3 tests/fixtures/sample_medical_record.py > ~/Desktop/sample_medical_record.txt
```

**Then in the app:**
1. Click **"Browse files"** in sidebar
2. Select `sample_medical_record.txt` from Desktop
3. Click **"Process Document"**

---

## Verification

### Check System Status

**1. Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

Should return JSON with model list.

**2. Verify Tesseract:**
```bash
tesseract --version
```

Should show version 4.x or 5.x.

**3. Verify Python environment:**
```bash
source venv/bin/activate  # if not already activated
python3 -c "import streamlit, pydantic, ollama, cryptography; print('✅ All imports successful')"
```

**4. Check log files:**
```bash
# Should be created after first run
ls -lh logs/
cat logs/audit.log | tail -5
```

---

### Test Core Features

**Run through this checklist:**

- [ ] Login with admin credentials
- [ ] Accept HIPAA consent
- [ ] Upload sample document
- [ ] View extracted patient data
- [ ] View extracted insurance info
- [ ] View extracted provider info
- [ ] View extracted diagnoses
- [ ] View extracted procedures
- [ ] Click "Suggest Medical Codes" (tests LLM)
- [ ] Generate CMS-1500 claim
- [ ] Validate claim (should pass)
- [ ] Ask chat question (tests LLM)
- [ ] Export claim to JSON

---

## Troubleshooting

### Common Issues

#### Issue 1: "ModuleNotFoundError: No module named 'streamlit'"

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

#### Issue 2: "Connection refused" or "Ollama not responding"

**Cause:** Ollama service not running

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve &

# Verify
ollama list
```

---

#### Issue 3: "Tesseract not found"

**Cause:** Tesseract not installed or not in PATH

**Solution:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr

# Verify
which tesseract
```

---

#### Issue 4: "Import errors" or "relative import beyond top-level package"

**Cause:** Python path not configured correctly

**Solution:** Already fixed in code with `sys.path.insert()`, but if you encounter:
```bash
# Make sure you're running from project root
cd ~/Desktop/Medvault-AI-Agent
streamlit run src/app.py
```

---

#### Issue 5: "404 Not Found" for Ollama models

**Cause:** Required models not downloaded

**Solution:**
```bash
# Download required model
ollama pull llama3.2

# Verify
ollama list
```

---

#### Issue 6: Port 8501 already in use

**Cause:** Another Streamlit instance running

**Solution:**
```bash
# Kill existing Streamlit processes
pkill -f "streamlit run"

# Or use different port
streamlit run src/app.py --server.port 8502
```

---

#### Issue 7: "Permission denied" errors

**Cause:** Incorrect directory permissions

**Solution:**
```bash
# Fix permissions
chmod 700 logs data uploads

# Verify
ls -ld logs data uploads
```

---

#### Issue 8: Tests failing with import errors

**Cause:** Test imports not finding modules

**Solution:** Already fixed in `tests/conftest.py`, but verify:
```bash
# Run from project root
cd ~/Desktop/Medvault-AI-Agent
source venv/bin/activate
pytest tests/ -v
```

---

#### Issue 9: Slow performance or high CPU usage

**Cause:** Ollama model running on CPU instead of GPU

**Solution:**
- **macOS:** Ollama automatically uses Apple Silicon GPU
- **Linux/Windows:** Install CUDA drivers for NVIDIA GPU
- **Alternative:** Use smaller model (but less accurate):
  ```bash
  ollama pull llama3.2:1b  # 1 billion parameter version
  ```

---

#### Issue 10: "CodeSuggestion object has no attribute 'metadata'"

**Cause:** Old cached version of code

**Solution:** Already fixed in latest version. Restart app:
```bash
pkill -f "streamlit run"
streamlit run src/app.py
```

---

### Getting Help

If you encounter other issues:

1. **Check logs:**
   ```bash
   tail -f logs/audit.log
   ```

2. **Enable debug mode:**
   ```bash
   LOG_LEVEL=DEBUG streamlit run src/app.py
   ```

3. **Review documentation:**
   - Architecture: `docs/architecture.md`
   - HIPAA Compliance: `docs/compliance.md`
   - Testing Guide: `TESTING.md`

4. **Open GitHub issue:**
   - Repository: https://github.com/12-crypto/Medvault-AI-Agent
   - Include error messages, logs, and system info

---

## Next Steps

### After Successful Setup:

1. **📖 Read the Documentation**
   - `README.md` - Project overview
   - `TESTING.md` - Comprehensive testing guide
   - `QUICK_TEST.md` - 5-minute quick start
   - `docs/architecture.md` - System design
   - `docs/compliance.md` - HIPAA requirements
   - `docs/cms1500_reference.md` - Form field guide

2. **🔒 Secure Your Installation**
   - Change default admin password
   - Rotate encryption keys regularly
   - Review `docs/compliance.md` for HIPAA requirements
   - Implement physical security controls
   - Set up backup procedures

3. **🧪 Test Thoroughly**
   - Run through `TESTING.md` test scenarios
   - Test with your own documents (de-identified!)
   - Verify all validation rules
   - Check audit logs are being written
   - Test error handling

4. **🚀 Deploy (If Production)**
   - Set up proper authentication (OAuth, SAML, etc.)
   - Configure external key management (AWS KMS, Azure Key Vault)
   - Implement database for persistent storage
   - Set up monitoring and alerting
   - Configure backups and disaster recovery
   - Review and sign Business Associate Agreements (BAAs)

5. **📊 Monitor and Maintain**
   - Review audit logs regularly
   - Update dependencies for security patches
   - Monitor system performance
   - Conduct periodic risk assessments
   - Train users on HIPAA policies

---

## Quick Reference Card

### Essential Commands

```bash
# Activate environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run application
make run
# OR
streamlit run src/app.py

# Run tests
pytest tests/ -v

# Check Ollama
ollama list
curl http://localhost:11434/api/tags

# View logs
tail -f logs/audit.log

# Stop application
pkill -f "streamlit run"  # macOS/Linux
Ctrl+C                    # Windows

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

### File Locations

| Item | Location |
|------|----------|
| Application | `src/app.py` |
| Configuration | `.env` |
| Logs | `logs/audit.log` |
| Encrypted data | `data/` |
| Uploads | `uploads/` |
| Documentation | `docs/` |
| Tests | `tests/` |
| Sample data | `tests/fixtures/` |

---

### Default Ports

| Service | Port |
|---------|------|
| Streamlit | 8501 |
| Ollama | 11434 |

---

### Support Resources

| Resource | Location |
|----------|----------|
| GitHub Issues | https://github.com/12-crypto/Medvault-AI-Agent/issues |
| Documentation | `docs/` directory |
| Testing Guide | `TESTING.md` |
| Quick Start | `QUICK_TEST.md` |
| Ollama Docs | https://ollama.com/docs |
| Streamlit Docs | https://docs.streamlit.io |

---

## Security Checklist

Before using with real data:

- [ ] Changed default admin password
- [ ] Generated new encryption key (not using example)
- [ ] Set up proper key management (KMS)
- [ ] Reviewed HIPAA compliance requirements
- [ ] Configured audit logging
- [ ] Set directory permissions to 700
- [ ] Disabled debug logging in production
- [ ] Set up physical security controls
- [ ] Trained users on HIPAA policies
- [ ] Executed Business Associate Agreements
- [ ] Implemented backup procedures
- [ ] Set up incident response plan
- [ ] Configured network security (firewall, VPN)
- [ ] Enabled encryption in transit (HTTPS/TLS)
- [ ] Scheduled regular security audits

---

## Version Info

- **MediVault AI Agent:** v1.0
- **Python Required:** 3.10+
- **Ollama Model:** llama3.2
- **Streamlit:** 1.50.0
- **Last Updated:** October 20, 2025

---

**🎉 Congratulations! You've successfully set up MediVault AI Agent!**

For questions or issues, please refer to the documentation or open a GitHub issue.

**⚠️ IMPORTANT DISCLAIMER:**

This software is for educational and research purposes only. It is NOT FDA-approved, NOT certified for production healthcare environments, and NOT a substitute for professional medical coding or billing services. Consult legal counsel and compliance professionals before using with real patient data. Use at your own risk.
