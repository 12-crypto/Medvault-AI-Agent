# 📋 MediVault AI Agent - Quick Reference

**Keep this handy for daily use!**

---

## 🚀 Essential Commands

### Start Application
```bash
cd ~/Desktop/Medvault-AI-Agent
source venv/bin/activate
streamlit run src/app.py
```

**Access:** http://localhost:8501

### Stop Application
```bash
# Press Ctrl+C in terminal
# OR
pkill -f "streamlit run"
```

---

## 🔑 Default Credentials

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `admin123` |

⚠️ **Change these in production!**

---

## 📂 Important Files & Directories

| Item | Path |
|------|------|
| **Main App** | `src/app.py` |
| **Config** | `.env` |
| **Audit Logs** | `logs/audit.log` |
| **Encrypted Data** | `data/` |
| **Uploads** | `uploads/` |
| **Sample File** | `~/Desktop/sample_medical_record.txt` |

---

## 🔧 Common Tasks

### View Audit Logs
```bash
tail -f logs/audit.log
```

### Check Ollama Status
```bash
ollama list
curl http://localhost:11434/api/tags
```

### Run Tests
```bash
pytest tests/ -v
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Generate New Encryption Key
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Import errors** | `source venv/bin/activate && pip install -r requirements.txt` |
| **Ollama not responding** | `ollama serve &` |
| **Port 8501 in use** | `pkill -f "streamlit run"` |
| **Tesseract not found** | `brew install tesseract` (macOS) |
| **Permission denied** | `chmod 700 logs data uploads` |

---

## 📊 Expected Processing Times

| Task | Time |
|------|------|
| **Upload & Parse** | 1-2 seconds |
| **Data Extraction** | 2-5 seconds |
| **Medical Coding (LLM)** | 10-20 seconds |
| **CMS-1500 Generation** | <1 second |
| **Full Workflow** | 30-60 seconds |

---

## ✅ Quick Test Checklist

- [ ] Login successful
- [ ] HIPAA consent accepted
- [ ] Document uploaded
- [ ] Patient data extracted
- [ ] Insurance data extracted
- [ ] Provider data extracted
- [ ] Diagnoses extracted
- [ ] Procedures extracted
- [ ] Medical codes suggested (LLM)
- [ ] CMS-1500 generated
- [ ] Validation passed
- [ ] Claim exported
- [ ] Chat assistant working

---

## 🔒 Security Reminders

- ✅ Keep `.env` file secure
- ✅ Change default password
- ✅ Review audit logs regularly
- ✅ Rotate encryption keys quarterly
- ✅ Never commit `.env` to git
- ✅ Use 700 permissions on sensitive directories
- ✅ Keep dependencies updated
- ✅ Review compliance checklist monthly

---

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| **[SETUP.md](SETUP.md)** | Complete installation guide |
| **[README.md](README.md)** | Project overview & features |
| **[TESTING.md](TESTING.md)** | Comprehensive testing guide |
| **[QUICK_TEST.md](QUICK_TEST.md)** | 5-minute test guide |
| **[docs/architecture.md](docs/architecture.md)** | System design |
| **[docs/compliance.md](docs/compliance.md)** | HIPAA requirements |
| **[docs/cms1500_reference.md](docs/cms1500_reference.md)** | Form field guide |

---

## 🆘 Getting Help

### Check Documentation
```bash
# View available docs
ls docs/
ls *.md
```

### Enable Debug Logging
```bash
LOG_LEVEL=DEBUG streamlit run src/app.py
```

### Report Issues
- GitHub: https://github.com/12-crypto/Medvault-AI-Agent/issues
- Include: Error message, logs, system info

---

## 🎯 Workflow Overview

```
1. Login → 2. Accept Consent → 3. Upload Document → 4. Review Data → 
5. Medical Coding → 6. Generate CMS-1500 → 7. Validate → 8. Export
```

**Estimated Time:** 2-5 minutes per claim

---

## 📞 Support

- **Documentation:** See `docs/` directory
- **Issues:** GitHub Issues
- **Security:** Report privately to security team

---

**Version:** 1.0 | **Last Updated:** October 20, 2025

**⚠️ DISCLAIMER:** Educational/research use only. Not for production healthcare without proper certifications, legal review, and BAAs.
