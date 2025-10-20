# 🚀 Quick Test Guide for MediVault AI Agent

## ✅ Sample File Ready!

I've created a sample medical record for you to test:

**Location:** `~/Desktop/sample_medical_record.txt`

---

## 📋 What's in the Sample File?

**Patient:** John Michael Doe (Synthetic/Fake data)
- DOB: 01/15/1980
- Sex: Male
- Address: 123 Main Street, Springfield, IL 62701

**Insurance:** Blue Cross Blue Shield
- Policy: ABC123456789
- Group: GRP001234

**Provider:** Dr. Jane Smith
- NPI: 1234567890
- Facility: Springfield Medical Center

**Visit Date:** 10/15/2024

**Diagnoses:**
1. **J20.9** - Acute bronchitis, unspecified
2. **I10** - Essential (primary) hypertension

**Procedures:**
1. **99213** - Office visit, established patient, moderate complexity ($150.00)
2. **94010** - Spirometry ($85.00)

**Total Charges:** $235.00

---

## 🧪 How to Test (5 Minutes)

### Step 1: Start the Application

```bash
cd /Users/dhruvrathee/Desktop/Medvault-AI-Agent
source venv/bin/activate
streamlit run src/app.py
```

**Or use Make:**
```bash
make run
```

### Step 2: Login

- Open browser to: http://localhost:8501
- **Username:** `admin`
- **Password:** `admin123`

### Step 3: Accept HIPAA Consent

- Review the consent dialog
- Select purpose: **Treatment** (or any option)
- Click "I Accept"

### Step 4: Upload Sample Document

1. Look for **"Upload Medical Document"** section in sidebar
2. Click **"Browse files"**
3. Navigate to your Desktop
4. Select **`sample_medical_record.txt`**
5. Click **"Process Document"**

### Step 5: Review Results

#### ✅ **OCR Results Tab**
- Should show: "Text extracted successfully"
- Confidence: ~100% (it's a text file)
- Character count: ~2,000 characters

#### ✅ **Patient Info Tab**
Expected results:
- **Name:** Doe, John
- **First Name:** John
- **Middle:** Michael
- **DOB:** 01/15/1980
- **Sex:** Male
- **Address:** 123 Main Street
- **City:** Springfield
- **State:** IL
- **Zip:** 62701

#### ✅ **Insurance Info Tab**
Expected results:
- **Payer Name:** Blue Cross Blue Shield
- **Policy Number:** ABC123456789
- **Group Number:** GRP001234
- **Relationship:** Self

#### ✅ **Provider Info Tab**
Expected results:
- **Provider Name:** Dr. Jane Smith
- **NPI:** 1234567890
- **Facility:** Springfield Medical Center
- **Facility NPI:** 9876543210
- **Tax ID:** 12-3456789

#### ✅ **Diagnoses Tab**
Expected results:
- **Code:** J20.9
- **Description:** Acute bronchitis, unspecified
- **Confidence:** High

- **Code:** I10
- **Description:** Essential hypertension
- **Confidence:** High

#### ✅ **Procedures Tab**
Expected results:
- **Code:** 99213
- **Description:** Office visit, established patient, moderate complexity
- **Charges:** $150.00

- **Code:** 94010
- **Description:** Spirometry
- **Charges:** $85.00

### Step 6: Medical Coding (Optional - Requires Ollama)

If you have `llama3.2` installed:

1. Scroll to **"Medical Coding Assistant"** section
2. Click **"Suggest Medical Codes"**
3. Wait 10-20 seconds
4. Review suggested codes with rationales and confidence scores
5. Accept or modify suggestions

**Note:** If you don't have llama3.2:
```bash
ollama pull llama3.2
```

### Step 7: Generate CMS-1500 Claim

1. Scroll to **"CMS-1500 Claim Generation"** section
2. Click **"Generate CMS-1500 Claim"**
3. Wait ~1 second

#### ✅ **Validation Results**
Expected:
- **Status:** ✅ Claim is valid (or minor warnings)
- **Errors:** 0 critical errors
- **Warnings:** 0-2 warnings (optional fields)

#### ✅ **Claim Preview**
Review the generated claim sections:

**Carrier/Payer Information:**
- Payer: Blue Cross Blue Shield

**Patient Demographics (Items 2-8):**
- Item 2 (Patient Name): Doe, John Michael
- Item 3 (DOB): 01 15 1980
- Item 3 (Sex): M
- Item 5 (Address): 123 Main Street, Springfield, IL 62701

**Insurance Information (Items 9-13):**
- Item 1a (Policy Number): ABC123456789
- Item 11 (Group Number): GRP001234

**Diagnoses (Item 21):**
- A: J20.9 - Acute bronchitis
- B: I10 - Essential hypertension
- ICD Indicator: 0 (ICD-10)

**Service Lines (Item 24):**
- Line 1:
  - Date: 10/15/24
  - Place: 11 (Office)
  - CPT: 99213
  - Diagnosis Pointer: AB
  - Charges: $150.00
  - Units: 1

- Line 2:
  - Date: 10/15/24
  - Place: 11
  - CPT: 94010
  - Diagnosis Pointer: A
  - Charges: $85.00
  - Units: 1

**Provider Information (Items 32-33):**
- Item 32 (Service Facility): Springfield Medical Center
- Item 32a (NPI): 9876543210
- Item 33 (Billing Provider): Dr. Jane Smith
- Item 33a (NPI): 1234567890

**Totals:**
- Item 28 (Total Charge): $235.00
- Item 29 (Amount Paid): $0.00

### Step 8: Export Claim (Optional)

1. Click **"Export to JSON"**
2. Download the JSON file
3. Review the structured claim data

### Step 9: Test Chat Interface (Optional)

Try asking the AI assistant:

**Sample Questions:**
- "What is Item 21 on the CMS-1500?"
- "Explain the difference between ICD-10 and CPT codes"
- "Why would my claim be rejected?"
- "What does diagnosis pointer AB mean?"

**Expected:** Helpful, context-aware responses about medical billing

---

## 🎯 Expected Results Summary

### ✅ What Should Work:
- ✅ Document upload and parsing
- ✅ Patient demographic extraction
- ✅ Insurance information extraction
- ✅ Provider information extraction
- ✅ Diagnosis code extraction (J20.9, I10)
- ✅ Procedure code extraction (99213, 94010)
- ✅ CMS-1500 claim generation
- ✅ Claim validation (should be valid or minor warnings)
- ✅ Claim preview with all sections populated
- ✅ Export to JSON

### ⚠️ What Requires Ollama (llama3.2):
- Medical coding suggestions with rationales
- Chat interface with AI assistant
- LLM-enhanced data extraction

### 🐛 Common Issues:

#### Issue: "No module named 'core'"
**Solution:** Make sure you started app from project root:
```bash
cd /Users/dhruvrathee/Desktop/Medvault-AI-Agent
streamlit run src/app.py
```

#### Issue: Ollama connection error
**Solution:** Make sure Ollama is running:
```bash
ollama list
# If not running:
ollama serve &
ollama pull llama3.2
```

#### Issue: File upload fails
**Solution:** Make sure the file exists:
```bash
ls -lh ~/Desktop/sample_medical_record.txt
```

#### Issue: Extraction returns empty data
**Expected:** Rule-based extraction should work. Some fields might be empty if pattern doesn't match exactly, but patient name, DOB, and insurance should be extracted.

---

## 📊 Performance Expectations

| Task | Expected Time |
|------|---------------|
| File upload | <1 second |
| Text parsing | <1 second |
| Data extraction (rule-based) | 2-5 seconds |
| Data extraction (with LLM) | 10-15 seconds |
| Medical coding (LLM) | 10-20 seconds |
| CMS-1500 generation | <1 second |
| Claim validation | <1 second |
| **Total E2E (without LLM)** | **5-10 seconds** |
| **Total E2E (with LLM)** | **30-60 seconds** |

---

## 🔍 What to Look For

### Data Quality Checks:

1. **Patient Name Parsing:**
   - ✅ Last, First Middle format
   - ✅ All three parts extracted

2. **Date Normalization:**
   - ✅ DOB converted to MM DD YYYY format
   - ✅ Service date converted correctly

3. **Code Validation:**
   - ✅ ICD-10 codes match pattern (letter + 2 digits + decimal + digits)
   - ✅ CPT codes are 5 digits

4. **Diagnosis Pointers:**
   - ✅ Service line 1 points to A and B (both diagnoses relevant)
   - ✅ Service line 2 points to A only (bronchitis related)

5. **Financial Calculations:**
   - ✅ Total charge = $150.00 + $85.00 = $235.00

6. **NPI Validation:**
   - ✅ Provider NPI is 10 digits
   - ✅ Facility NPI is 10 digits

---

## 🎓 Learning Objectives

After this test, you should understand:

1. **Document Processing Flow:**
   - Upload → Parse → Extract → Code → Generate → Validate

2. **CMS-1500 Structure:**
   - Patient demographics (Items 2-8)
   - Insurance information (Items 9-13)
   - Diagnoses (Item 21)
   - Service lines (Item 24)
   - Provider information (Items 32-33)

3. **Medical Coding Basics:**
   - ICD-10 codes represent diagnoses
   - CPT codes represent procedures
   - Diagnosis pointers link procedures to justifying diagnoses

4. **Validation Rules:**
   - Required fields must be present
   - Formats must match specifications
   - Diagnosis pointers must reference valid diagnoses
   - Totals must calculate correctly

---

## 🚀 Next Steps

After successful test:

1. **Try with your own documents** (de-identified or synthetic)
2. **Install llama3.2** for LLM features
3. **Review validation errors** and learn CMS-1500 rules
4. **Explore chat interface** for billing questions
5. **Check audit logs** in `logs/audit.log`
6. **Review comprehensive guide** in `TESTING.md`

---

## 📞 Need Help?

- **Full Testing Guide:** See `TESTING.md`
- **Architecture:** See `docs/architecture.md`
- **HIPAA Compliance:** See `docs/compliance.md`
- **CMS-1500 Reference:** See `docs/cms1500_reference.md`

---

**Happy Testing! 🎉**

Your sample file is ready at: **`~/Desktop/sample_medical_record.txt`**

Just drag and drop it into the Streamlit app!
