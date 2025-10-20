# HIPAA Compliance Documentation

## Overview

MediVault AI Agent implements **Privacy and Security controls** aligned with the HIPAA Security Rule (45 CFR Part 164, Subpart C) for covered entities handling Protected Health Information (PHI).

**Important:** This documentation describes technical safeguards implemented in the software. **Full HIPAA compliance** requires organizational policies, procedures, business associate agreements, and risk assessments that are the **customer's responsibility**.

---

## HIPAA Security Rule Implementation

### Administrative Safeguards (§164.308)

#### ✅ Security Management Process (§164.308(a)(1))

**Risk Analysis (Required)**
- **Customer Responsibility:** Conduct formal risk analysis per §164.308(a)(1)(ii)(A)
- **Tool Support:** Application provides audit logs for review

**Risk Management (Required)**
- **Implemented:** 
  - At-rest encryption (Fernet/AES-128)
  - Access controls and authentication
  - Audit logging
- **Customer Responsibility:** Develop risk management policies

**Sanction Policy (Required)**
- **Customer Responsibility:** Establish sanctions for security violations
- **Tool Support:** Audit logs document policy violations

**Information System Activity Review (Required)**
- **Implemented:** Comprehensive audit logging (`logs/audit.log`)
- **Format:** Structured JSON with timestamp, user, resource, action, result
- **Review:** Customer must establish regular review procedures

#### ✅ Assigned Security Responsibility (§164.308(a)(2))
- **Customer Responsibility:** Designate a Security Official
- **Tool Support:** Admin role in application for security oversight

#### ⚠️ Workforce Security (§164.308(a)(3))
- **Authorization/Supervision (Addressable):** 
  - Implemented: Role-based access control (admin, provider, staff, readonly)
  - Customer must document workforce authorization procedures
- **Workforce Clearance (Addressable):** Customer responsibility
- **Termination Procedures (Addressable):** 
  - Tool: Admin can disable user accounts
  - Customer must document termination procedures

#### ⚠️ Information Access Management (§164.308(a)(4))
- **Access Authorization (Addressable):**
  - Implemented: Role-based authorization
  - Customer must document access authorization procedures
- **Access Establishment/Modification (Addressable):**
  - Tool: User management via AuthManager
  - Customer responsibility to document procedures

#### ✅ Security Awareness and Training (§164.308(a)(5))
- **Customer Responsibility:** Provide HIPAA training to workforce
- **Recommendation:** Include training on:
  - PHI handling in this application
  - Consent requirements
  - Minimum necessary principle
  - Audit log review

#### ⚠️ Security Incident Procedures (§164.308(a)(6))
- **Response and Reporting (Required):**
  - Tool: Audit logs capture security events
  - Customer must establish incident response procedures
  - **Recommendation:** Monitor audit logs for:
    - Failed login attempts
    - Permission denied events
    - Unusual access patterns

#### ✅ Contingency Plan (§164.308(a)(7))
- **Data Backup (Required):**
  - Tool: Encrypted PHI storage in `data/phi/`
  - Customer must implement backup procedures
- **Disaster Recovery (Required):** Customer responsibility
- **Emergency Mode (Required):** Admin account provides emergency access
- **Testing/Revision (Addressable):** Customer responsibility

#### ⚠️ Evaluation (§164.308(a)(8))
- **Required:** Periodic technical and non-technical evaluations
- **Customer Responsibility:** Conduct annual security evaluations
- **Tool Support:** Review audit logs, validation error rates, access patterns

#### ⚠️ Business Associate Contracts (§164.308(b))
- **Customer Responsibility:** 
  - Execute BAAs with any third-party service providers
  - **Note:** This application runs locally with no external services by default
  - If integrating with external systems (payer APIs, code databases), BAA required

---

### Physical Safeguards (§164.310)

#### ⚠️ Facility Access Controls (§164.310(a))
- **Customer Responsibility:** Physical security of servers/workstations
- **Recommendations:**
  - Restrict physical access to devices running application
  - Implement video surveillance, locks, badge systems as appropriate
  - Document facility access procedures

#### ⚠️ Workstation Use (§164.310(b))
- **Customer Responsibility:** Policies for workstation use
- **Recommendations:**
  - Lock workstations when unattended
  - Use privacy screens in shared areas
  - Restrict PHI display to authorized users

#### ⚠️ Workstation Security (§164.310(c))
- **Customer Responsibility:** Physical safeguards for workstations
- **Tool Support:** Application can be configured for automatic logoff
- **Recommendations:**
  - Enable screen lock/timeout
  - Secure workstations to prevent theft

#### ⚠️ Device and Media Controls (§164.310(d))
- **Disposal (Required):**
  - Tool: Secure deletion of PHI records via `delete_phi()`
  - Customer must document disposal procedures
- **Media Re-use (Required):** 
  - Tool: Encrypted storage prevents data recovery from media
- **Accountability (Addressable):** Customer maintains hardware inventory
- **Data Backup/Storage (Addressable):** Customer responsibility

---

### Technical Safeguards (§164.312)

#### ✅ Access Control (§164.312(a)(1)) - **IMPLEMENTED**

**Unique User Identification (Required) - §164.312(a)(2)(i)**
- ✅ **Implemented:** Username-based authentication
- Each user has unique credentials
- Audit logs track actions by username

**Emergency Access Procedure (Required) - §164.312(a)(2)(ii)**
- ✅ **Implemented:** Admin role has full access
- Can be used for emergency access to PHI
- All emergency access logged in audit trail

**Automatic Logoff (Addressable) - §164.312(a)(2)(iii)**
- ⚠️ **Partially Implemented:** Streamlit session management
- **Customer Configuration:** Set `server.sessionState.maxAge` in Streamlit config
- **Recommendation:** 15-30 minute timeout for unattended sessions

**Encryption and Decryption (Addressable) - §164.312(a)(2)(iv)**
- ✅ **Implemented:** Fernet (AES-128-CBC) encryption for PHI at rest
- Encryption key management via environment variable
- All PHI stored in `data/phi/` is encrypted
- File permissions set to 0o600 (owner read/write only)

#### ✅ Audit Controls (§164.312(b)) - **IMPLEMENTED**
- ✅ **Comprehensive audit logging** to `logs/audit.log`
- **Logged Events:**
  - PHI access (read, create, update, delete, export)
  - Authentication (successful and failed)
  - Authorization failures (permission denied)
  - Consent given/revoked
- **Log Format:** Structured JSON with:
  - Timestamp (UTC)
  - User ID
  - Resource accessed
  - Action performed
  - Result (success/failure/denied)
  - Metadata (context)
- **Retention:** Customer must define log retention period
- **Review:** Customer must establish regular audit log review process

#### ✅ Integrity (§164.312(c)(1))
- **Mechanism to Authenticate ePHI (Addressable):**
  - ✅ Encrypted storage ensures data integrity (tampering detected by decryption failure)
  - ✅ Audit logs provide integrity trail (who changed what, when)
  - ⚠️ **Enhancement:** Could add cryptographic signatures for stronger integrity

#### ✅ Person or Entity Authentication (§164.312(d)) - **IMPLEMENTED**
- ✅ **Password-based authentication**
- Passwords hashed with PBKDF2-HMAC-SHA256 (100,000 iterations)
- Salted hashes prevent rainbow table attacks
- **Recommendation for Production:**
  - Add two-factor authentication (2FA)
  - Integrate with enterprise identity provider (LDAP, SAML, OIDC)
  - Enforce password complexity requirements

#### ⚠️ Transmission Security (§164.312(e))
- **Integrity Controls (Addressable):**
  - ⚠️ **Local Deployment Only:** Default runs on localhost (no network transmission)
  - ⚠️ **LAN Deployment:** Customer must enable TLS
  - Set `TLS_ENABLED=true` in `.env`
  - Provide certificate: `TLS_CERT_PATH` and `TLS_KEY_PATH`
- **Encryption (Addressable):**
  - ⚠️ If deploying beyond localhost, **TLS 1.2+ is required**
  - Use strong cipher suites (AES-128-GCM or stronger)
  - Disable weak protocols (SSLv3, TLS 1.0, TLS 1.1)

---

## Organizational Requirements

### ⚠️ Business Associate Agreement (§164.504(e))
- **Applies if:** MediVault AI Agent processes PHI on behalf of a covered entity
- **Customer Responsibility:** Execute BAA with any business associates
- **Clarification:** 
  - Local-only deployment: No BAA needed (internal system)
  - Hosting provider: BAA required if hosted by third party
  - Ollama: Local service, no BAA needed
  - External integrations (payer APIs, cloud storage): BAA required

---

## Privacy Rule Considerations

While this is primarily a Security Rule implementation, relevant Privacy Rule requirements:

### ⚠️ Minimum Necessary (§164.502(b))
- ✅ **Implemented:** `PolicyManager.apply_minimum_necessary()`
- Configurable via `MINIMUM_NECESSARY_MODE=true` in `.env`
- Filters PHI fields based on purpose (treatment, payment, operations)
- **Customer Responsibility:** Define minimum necessary policies per use case

### ⚠️ Individual Rights
- **Access (§164.524):** Customer must provide mechanism for patients to access their PHI
- **Amendment (§164.526):** Customer must establish amendment procedures
- **Accounting (§164.528):** Audit logs support accounting of disclosures

### ✅ Consent Management
- ✅ **Implemented:** Explicit consent dialog for PHI processing
- Consent tracked per patient, per purpose
- Consent logged in audit trail
- **Types:** treatment, payment, operations, LLM processing, data sharing
- User can revoke consent at any time

### ⚠️ Notice of Privacy Practices (§164.520)
- **Customer Responsibility:** Provide patients with Notice of Privacy Practices
- Must describe how PHI is used and protected

---

## Online Tracking Technology Guidance

Per HHS OCR Guidance (December 2022):

### ✅ **COMPLIANT:** No Tracking Technologies
- ❌ No Google Analytics
- ❌ No Meta Pixel
- ❌ No third-party cookies
- ❌ No external JavaScript
- ❌ No user tracking or profiling
- ✅ `--browser.gatherUsageStats=false` (Streamlit config)

### ⚠️ **WARNING for Covered Entities**
If deploying as a covered entity website, **do not add:**
- Marketing pixels
- Social media plugins
- Advertising scripts
- Analytics that track IP, geolocation, or browsing behavior

---

## Data Retention and Disposal

### ⚠️ Customer Responsibilities
- **Retention Period:** Define per organizational policy (default: 90 days)
- **Configuration:** Set `PHI_RETENTION_DAYS` in `.env`
- **Disposal Procedure:**
  - Application provides `delete_phi()` function
  - Customer must document disposal procedures
  - Consider secure erasure of backup media

### ✅ Automated Retention Check
- `PolicyManager.should_retain(record_date)` checks age against policy
- Customer must implement automated deletion process

---

## Configuration Checklist

### Required Configuration

1. **Encryption Keys**
   ```bash
   # Generate encryption key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Add to .env
   ENCRYPTION_KEY=<generated_key>
   ```

2. **Session Security**
   ```bash
   # Generate session secret
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Add to .env
   SESSION_SECRET=<generated_secret>
   ```

3. **Audit Logging**
   ```bash
   # Enable audit logging
   AUDIT_ENABLED=true
   AUDIT_LOG_PATH=./logs/audit.log
   ```

4. **PHI Storage**
   ```bash
   DB_PATH=./data/medivault.db
   DB_ENCRYPTION=true
   PHI_RETENTION_DAYS=90
   ```

5. **Minimum Necessary**
   ```bash
   MINIMUM_NECESSARY_MODE=true
   ```

6. **TLS (if not localhost)**
   ```bash
   TLS_ENABLED=true
   TLS_CERT_PATH=/path/to/cert.pem
   TLS_KEY_PATH=/path/to/key.pem
   ```

---

## Customer Responsibilities Summary

### Must Implement
- [ ] Conduct risk analysis (§164.308(a)(1)(ii)(A))
- [ ] Designate Security Official (§164.308(a)(2))
- [ ] Establish workforce authorization procedures (§164.308(a)(3))
- [ ] Provide HIPAA security awareness training (§164.308(a)(5))
- [ ] Create incident response procedures (§164.308(a)(6))
- [ ] Implement data backup plan (§164.308(a)(7))
- [ ] Conduct annual security evaluation (§164.308(a)(8))
- [ ] Execute Business Associate Agreements if applicable (§164.308(b))
- [ ] Implement physical access controls (§164.310(a))
- [ ] Document workstation use and security policies (§164.310(b-c))
- [ ] Establish media disposal procedures (§164.310(d))
- [ ] Configure automatic logoff (§164.312(a)(2)(iii))
- [ ] Review audit logs regularly (§164.312(b))
- [ ] Enable TLS if not localhost (§164.312(e))
- [ ] Provide Notice of Privacy Practices (§164.520)
- [ ] Define and enforce minimum necessary policies (§164.502(b))

### Strongly Recommended
- [ ] Enable two-factor authentication
- [ ] Integrate with enterprise identity provider
- [ ] Implement automated PHI retention/deletion
- [ ] Set up SIEM integration for audit logs
- [ ] Conduct penetration testing
- [ ] Create disaster recovery and business continuity plans
- [ ] Document all security policies and procedures
- [ ] Train staff on application-specific security procedures

---

## Compliance Attestation

**MediVault AI Agent provides technical safeguards** that support HIPAA compliance. However:

❗ **This software alone does not make an organization HIPAA-compliant.**

Full compliance requires:
1. ✅ Technical safeguards (implemented in this software)
2. ⚠️ Administrative safeguards (policies, training, risk analysis)
3. ⚠️ Physical safeguards (facility security, device controls)
4. ⚠️ Organizational requirements (BAAs, contracts)
5. ⚠️ Privacy practices (notices, consent, individual rights)

**Customers are responsible** for items 2-5 and for proper configuration and use of this software per their organizational policies.

---

## Audit and Assessment

### Internal Audit Recommendations
- Review audit logs monthly for unusual access patterns
- Validate encryption is enabled for all PHI storage
- Test backup and recovery procedures quarterly
- Review and update access permissions quarterly
- Conduct annual security risk assessment

### External Assessment
- Consider engaging qualified independent assessor
- Penetration testing annually
- HIPAA Security Rule gap analysis
- Privacy Rule compliance review

---

## Contact and Support

For HIPAA compliance questions related to this software:
- Review this documentation
- Consult with qualified HIPAA compliance professional
- Legal counsel for BAA and policy guidance

For software security issues:
- Review `docs/architecture.md`
- Check audit logs
- File GitHub issue (do not include PHI in issue reports!)

---

**Disclaimer:** This documentation is provided for informational purposes and does not constitute legal advice. Consult with qualified legal and compliance professionals for your specific HIPAA obligations.
