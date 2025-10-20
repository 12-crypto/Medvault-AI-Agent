# CMS-1500 Form Reference

## Overview

The CMS-1500 (02/12 version) is the standard paper claim form used by healthcare providers to bill Medicare, Medicaid, and many private insurance carriers. This document provides field-by-field guidance aligned with NUCC specifications.

## Form Version

**Current:** CMS-1500 (02/12) - approved by the National Uniform Claim Committee (NUCC)

**References:**
- NUCC 1500 Instruction Manual: https://www.nucc.org/
- Medicare Claims Processing Manual, Chapter 26: https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Downloads/clm104c26.pdf
- CMS Internet-Only Manual (IOM) Pub 100-04

---

## Field-by-Field Guide

### Carrier/Payer Information (Top Section)
Location for insurance company name and address (right-aligned header).

---

### Item 1: Type of Insurance
**Check one box:**
- ☐ Medicare
- ☐ Medicaid  
- ☐ TRICARE (CHAMPUS)
- ☐ CHAMPVA
- ☐ Group Health Plan
- ☐ FECA (Federal Employee Compensation Act)
- ☐ Other

**Rules:**
- Only one box can be checked
- Determines which payer instructions apply

---

### Item 1a: Insured's ID Number
**Required**

The patient's identification number as it appears on their insurance card.

**Format:** Alphanumeric, up to 29 characters
**Examples:** 
- Medicare: 1234567890A (11 characters)
- Medicaid: State-specific format
- Commercial: Policy number from card

**Validation:** Cannot be blank

---

### Item 2: Patient's Name
**Required**

Last name, first name, middle initial (exactly as on insurance card).

**Format:** LAST, FIRST MI
**Example:** DOE, JOHN M
**Max Length:** Last=35, First=25, MI=1

---

### Item 3: Patient's Birth Date and Sex
**Required**

**Date Format:** MM DD YYYY (spaces, not slashes)
**Example:** 01 15 1980

**Sex:** M (Male), F (Female), U (Unknown)

**Validation:**
- Date must be valid calendar date
- Patient must be born before date of service

---

### Item 4: Insured's Name
If patient is not the insured (e.g., spouse's insurance), enter insured's name.

**Format:** LAST, FIRST MI
**Leave blank** if Item 6 indicates "Self"

---

### Item 5: Patient's Address
Street address, city, state, ZIP code, phone number.

**Format:**
- Address line 1: Street
- Address line 2: City, State ZIP
- Phone: (XXX) XXX-XXXX

**Max Length:** Address=55, City=30, State=2, ZIP=15

---

### Item 6: Patient Relationship to Insured
**Required**

Check one:
- ☐ Self
- ☐ Spouse
- ☐ Child
- ☐ Other

**Impact:** If "Self", Item 4 should be blank and insured information (Items 7, 11a-d) should match patient.

---

### Item 7: Insured's Address
Insured's address (if different from patient).

**Leave blank** if Item 6 = "Self" (use patient's address from Item 5)

---

### Item 8: Reserved for NUCC Use
**Optional checkboxes for patient status:**
- Marital status: Single, Married, Other
- Employment status: Employed, Full-Time Student, Part-Time Student

**Note:** Some payers do not require this field.

---

### Item 9: Other Insured's Name
If patient has secondary insurance, enter other insured's name.

**Coordination of Benefits:** Used when multiple insurance policies cover patient.

---

### Item 9a-d: Other Insured's Information
- **9a:** Other insured's policy or group number
- **9b:** Reserved (other insured's DOB, sex)
- **9c:** Reserved (employer name or school name)
- **9d:** Insurance plan name or program name

---

### Item 10: Is Patient's Condition Related To:

#### Item 10a: Employment?
☐ Yes ☐ No

Workers' compensation indicator.

#### Item 10b: Auto Accident?
☐ Yes ☐ No

If Yes, enter 2-letter state code where accident occurred.

**Validation:** If Yes, state code required (e.g., IL, CA)

#### Item 10c: Other Accident?
☐ Yes ☐ No

#### Item 10d: Claim Codes
**Designated by NUCC** - varies by payer. Often used for Medicaid-specific identifiers.

---

### Item 11: Insured's Policy Group or FECA Number
Group number from insurance card.

**Required for group health plans.**

---

### Item 11a: Insured's Date of Birth, Sex
If patient is not the insured (Item 6 ≠ Self), enter insured's DOB and sex.

**Format:** MM DD YYYY, M/F/U

---

### Item 11b: Other Claim ID
**Designated by NUCC** - varies by payer. May be used for prior authorization or referral numbers.

---

### Item 11c: Insurance Plan Name or Program Name
Name of the patient's insurance plan.

**Example:** BlueCross BlueShield PPO

---

### Item 11d: Is There Another Health Benefit Plan?
☐ Yes ☐ No

If Yes, complete Items 9a-9d.

---

### Item 12: Patient's or Authorized Person's Signature
**Standard entry:** "Signature on File" or actual signature

Authorizes release of information and payment to provider.

**HIPAA:** Must have authorization on file (can be electronic).

---

### Item 13: Insured's or Authorized Person's Signature
**Standard entry:** "Signature on File"

Authorizes payment directly to provider.

---

### Item 14: Date of Current Illness, Injury, or Pregnancy (LMP)
**Format:** MM DD YYYY

**Qualifier codes:**
- **431:** Onset of current symptoms/illness
- **484:** Last menstrual period (pregnancy)

**Example:** 10 01 2024 (qualifier: 431)

---

### Item 15: Other Date
**Format:** MM DD YYYY

Qualifier codes vary by payer. Commonly used for:
- Date of similar illness
- Initial treatment date

---

### Item 16: Dates Patient Unable to Work
**Format:** MM DD YYYY TO MM DD YYYY

Used for disability claims.

**Example:** 10 15 2024 TO 10 22 2024

---

### Item 17: Name of Referring Provider or Other Source
Referring physician's name (if applicable).

**Format:** Last, First

**Note:** Not required for all service types (e.g., primary care visits).

---

### Item 17a: ID Number of Referring Provider (Legacy)
**Deprecated** - use 17b for NPI.

---

### Item 17b: NPI of Referring Provider
**10-digit National Provider Identifier**

**Required if:** Item 17 is filled.

**Validation:** Must be valid 10-digit NPI.

**Example:** 1234567890

---

### Item 18: Hospitalization Dates Related to Current Services
**Format:** MM DD YYYY TO MM DD YYYY

Inpatient hospital admission and discharge dates (if applicable).

**Example:** 10 10 2024 TO 10 12 2024

---

### Item 19: Additional Claim Information
**Designated by NUCC** - varies by payer.

**Common uses:**
- Demonstration project identifiers
- Additional diagnosis information
- Qualifier codes

**Max Length:** 80 characters

---

### Item 20: Outside Lab? $ Charges
**If purchased services (e.g., lab work) from outside lab:**
☐ Yes ☐ No

If Yes, enter charges: $______

---

### Item 21: Diagnosis or Nature of Illness or Injury
**CRITICAL FIELD**

**ICD Indicator:**
- **0** = ICD-10-CM (current standard)
- **9** = ICD-9-CM (legacy, deprecated)

**Diagnosis Codes A-L (up to 12):**

**Format:** ICD-10 code (e.g., J20.9, I10, E11.9)

**ICD-10 Structure:**
- 3-7 alphanumeric characters
- Letter (A-Z except U) + 2 digits + optional decimal + 1-4 more digits
- **Examples:**
  - J20.9 - Acute bronchitis, unspecified
  - I10 - Essential hypertension
  - E11.9 - Type 2 diabetes without complications

**Rules:**
- At least one diagnosis required
- List in order of priority (A = primary)
- Maximum 12 diagnoses

**Validation:**
- Must follow ICD-10-CM format
- Code must be valid in current version
- Use most specific code available (avoid .9 unspecified when specifics known)

**Medicare-Specific:**
- Item 21 diagnosis codes must support medical necessity for services in Item 24

---

### Item 22: Resubmission Code and Original Ref. No.
**For corrected or replacement claims:**
- Resubmission code (varies by payer)
- Original claim reference number

**Leave blank for original submissions.**

---

### Item 23: Prior Authorization Number
Prior authorization or referral number if required by payer.

**Max Length:** 30 characters

**Validation:** Required if payer mandates pre-authorization for services billed.

---

### Item 24: Service Lines (A-J)
**UP TO 6 LINES** - Most complex section

Each line represents a service/procedure. Columns:

#### Item 24A: Date(s) of Service
**Format:** MM DD YY TO MM DD YY

**From:** Date service began
**To:** Date service ended (can be same as From for single-day service)

**Example:** 10 15 24 TO 10 15 24

#### Item 24B: Place of Service (POS)
**2-digit code**

**Common codes:**
- **11:** Office
- **12:** Home
- **21:** Inpatient hospital
- **22:** On-campus outpatient hospital
- **23:** Emergency room
- **31:** Skilled nursing facility
- **81:** Independent laboratory

**Full list:** https://www.cms.gov/Medicare/Coding/place-of-service-codes

#### Item 24C: EMG (Emergency)
**Optional:** Y (Yes) if emergency service

**Leave blank** for non-emergency.

#### Item 24D: Procedures, Services, or Supplies (CPT/HCPCS)
**CPT or HCPCS code + modifiers**

**CPT:** 5-digit code (e.g., 99213)
**HCPCS:** Letter + 4 digits (e.g., G0008) or 5-digit CPT

**Modifiers (up to 4):** 2-character codes that provide additional information

**Examples:**
- 99213 - Office visit, established patient, moderate complexity
- 99213-25 - Significant, separately identifiable E/M service
- 80053 - Comprehensive metabolic panel
- 94010-59 - Spirometry, distinct procedural service

**Validation:**
- Code must be valid CPT/HCPCS
- Modifiers must be valid and appropriate for code

#### Item 24E: Diagnosis Pointer
**1-4 LETTERS (A, B, C, D, E, F, G, H, I, J, K, L)**

Links service to diagnosis code(s) from Item 21.

**Examples:**
- A - Links to diagnosis code in Item 21A
- AB - Links to diagnoses in 21A and 21B
- ABD - Links to diagnoses in 21A, 21B, and 21D

**Rules:**
- At least one pointer required
- Can reference up to 4 diagnoses per line
- All pointers must reference non-empty diagnosis fields

**Validation:**
- Diagnosis pointer letters must reference filled Item 21 fields
- Medicare requires diagnosis-procedure linkage to justify medical necessity

#### Item 24F: $ Charges
**Dollar amount for this service line**

**Format:** Decimal with 2 places (e.g., 150.00)

**Do not include dollar sign** in electronic submissions.

#### Item 24G: Days or Units
**Number of times service was performed**

**Examples:**
- 1 - Single office visit
- 10 - 10 physical therapy sessions
- 5 - 5 units of a supply item

**Default:** 1 (if not specified)

#### Item 24H: EPSDT Family Plan
**For Medicaid EPSDT (Early and Periodic Screening, Diagnostic and Treatment) services**

Codes vary by state.

**Leave blank** for non-Medicaid.

#### Item 24I: ID Qualifier
**Qualifier for rendering provider ID in 24J**

**Common values:**
- **Blank or 0B:** State license number
- **1G:** Provider UPIN (legacy)
- **Leave blank** when 24J contains NPI

#### Item 24J: Rendering Provider ID #
**10-digit NPI** of individual who rendered service

**Required by Medicare and most payers**

**Validation:** Must be valid 10-digit NPI

**Example:** 1234567890

**Note:** Can be same as billing provider (Item 33a) for solo practitioners.

---

### Item 25: Federal Tax ID Number
**EIN or SSN** of billing provider

**Format:**
- EIN: XX-XXXXXXX (9 digits)
- SSN: XXX-XX-XXXX (9 digits)

**Checkboxes:**
- ☐ SSN
- ☐ EIN

**Validation:**
- Must be 9 digits (hyphens optional)
- EIN preferred over SSN

---

### Item 26: Patient's Account No.
**Optional** - Provider's internal account number

**Max Length:** 15 characters

**Helps track claim in provider's system**

---

### Item 27: Accept Assignment?
☐ Yes ☐ No

**Yes:** Provider agrees to accept insurance payment as payment in full (minus patient responsibility).

**Medicare:** Most providers are required to accept assignment.

---

### Item 28: Total Charge
**Sum of all charges from Item 24F**

**Format:** Decimal with 2 places

**Validation:** Should equal sum of all line items (Item 24F, lines 1-6)

**Example:** If 24F lines are $150.00, $85.00 → Total = $235.00

---

### Item 29: Amount Paid
**Amount patient or other payers have already paid**

**Format:** Decimal with 2 places

**Leave 0.00** if no payment yet made.

---

### Item 30: Reserved for NUCC Use (Balance Due)
**Calculated:** Item 28 (Total Charge) - Item 29 (Amount Paid)

**Note:** Most payers do not require this field.

---

### Item 31: Signature of Physician or Supplier
**Standard entry:** "Signature on File" or actual signature

**Date:** Date claim signed (format: MM DD YYYY)

**Certifies services were rendered as described**

---

### Item 32: Service Facility Location Information
**Where services were rendered** (if different from billing provider)

**Format:**
- Name
- Address
- City, State ZIP

**Item 32a: NPI** (10 digits, required)
**Item 32b: Other ID** (legacy, often blank)

**Validation:** NPI required if services performed at facility different from Item 33.

**Example:**
```
Springfield Medical Center
456 Healthcare Dr
Springfield, IL 62701
NPI: 9876543210
```

---

### Item 33: Billing Provider Info & Ph #
**REQUIRED** - Provider submitting the claim

**Format:**
- Name
- Address
- City, State ZIP
- Phone: (XXX) XXX-XXXX

**Item 33a: NPI** (10 digits, REQUIRED)
**Item 33b: Other ID** (legacy, often blank)

**Validation:**
- NPI is required
- Must be valid 10-digit NPI
- Phone number should include area code

**Example:**
```
Dr. Jane Smith
123 Provider Lane
Springfield, IL 62701
(555) 123-4567
NPI: 1234567890
```

---

## Common Validation Errors

### Critical Errors (Claim will be rejected)
1. **Missing required fields:**
   - Items 1a, 2, 3, 21 (at least one diagnosis), 24 (at least one line), 33a (billing NPI)

2. **Invalid formats:**
   - NPI not 10 digits
   - ICD-10 code format invalid
   - CPT code format invalid
   - Dates not in MM DD YYYY format

3. **Diagnosis pointer errors:**
   - Pointer references empty diagnosis field
   - No diagnosis pointer for service line

4. **Total charge mismatch:**
   - Item 28 doesn't equal sum of Item 24F

### Warnings (May cause delays)
1. **Specificity issues:**
   - Using unspecified codes (.9) when more specific available

2. **Medical necessity:**
   - Diagnosis doesn't support procedure (e.g., annual physical diagnosis linked to emergency surgery)

3. **Duplicate codes:**
   - Same diagnosis listed multiple times

4. **Missing recommended fields:**
   - Prior authorization (Item 23) when required by payer
   - Referring provider NPI (Item 17b) when referral exists

---

## Payer-Specific Requirements

### Medicare
- Accept assignment usually required (Item 27 = Yes)
- NPI required in Items 17b, 24J, 32a, 33a
- Signature on file acceptable (Items 12, 13, 31)
- ICD indicator must be 0 (ICD-10)

### Medicaid
- Varies by state
- May require EPSDT codes (Item 24H)
- May require claim codes (Item 10d)

### Commercial Payers
- Verify specific requirements with each payer
- Prior authorization often required (Item 23)
- May require referral numbers

---

## Best Practices

1. **Always use most specific diagnosis code available**
2. **Link diagnoses to procedures logically** (medical necessity)
3. **Verify all NPIs** in NPPES database: https://npiregistry.cms.hhs.gov/
4. **Check code validity** against current ICD-10-CM and CPT books
5. **Keep documentation** supporting all billed services
6. **Review claim before submission** using validation tools
7. **Train staff** on proper completion of all fields
8. **Update procedures** when CMS/NUCC releases new versions

---

## Resources

- **NUCC Website:** https://www.nucc.org/
- **CMS Claims Manual:** https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Internet-Only-Manuals-IOMs
- **NPI Registry:** https://npiregistry.cms.hhs.gov/
- **ICD-10-CM Codes:** https://www.cdc.gov/nchs/icd/icd-10-cm.htm
- **CPT Codes:** https://www.ama-assn.org/practice-management/cpt
- **Place of Service Codes:** https://www.cms.gov/Medicare/Coding/place-of-service-codes

---

## Version History

- **CMS-1500 (08/05):** Legacy version
- **CMS-1500 (02/12):** Current version (implemented in MediVault AI Agent)
- **Future:** NUCC reviews form periodically; check for updates

---

**Note:** This reference is for educational purposes. Always consult official NUCC instructions and payer-specific guidelines for authoritative requirements.
