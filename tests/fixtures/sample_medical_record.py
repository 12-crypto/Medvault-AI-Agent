"""
Sample Synthetic Medical Record (Text Format)
For testing purposes only - contains NO real patient data
"""

SAMPLE_MEDICAL_RECORD_TEXT = """
MEDICAL RECORD - SYNTHETIC DATA FOR TESTING ONLY

Patient Information:
Patient Name: John Michael Doe
Date of Birth: 01/15/1980
Sex: Male
Address: 123 Main Street
City: Springfield
State: IL
Zip Code: 62701
Phone: (555) 123-4567

Insurance Information:
Insurance Company: Blue Cross Blue Shield
Policy Number: ABC123456789
Group Number: GRP001234
Subscriber: Self

Provider Information:
Provider Name: Dr. Jane Smith
Provider NPI: 1234567890
Facility Name: Springfield Medical Center
Facility NPI: 9876543210
Facility Address: 456 Healthcare Drive, Springfield, IL 62701
Tax ID: 12-3456789

Visit Information:
Date of Service: 10/15/2024
Place of Service: Office (11)

Chief Complaint:
Patient presents with persistent cough and fever for 3 days.

Diagnoses:
1. J20.9 - Acute bronchitis, unspecified
2. I10 - Essential (primary) hypertension

Procedures:
1. 99213 - Office visit, established patient, moderate complexity
2. 94010 - Spirometry

Charges:
- 99213: $150.00
- 94010: $85.00
Total: $235.00

Clinical Notes:
45-year-old male presents with productive cough and low-grade fever (100.2°F) 
for the past 3 days. Patient reports yellow-green sputum and mild chest 
discomfort. Denies shortness of breath at rest.

Past medical history significant for hypertension, well-controlled on medication.
No known drug allergies. Non-smoker.

Physical examination reveals clear bilateral breath sounds with scattered rhonchi.
No wheezing appreciated. Cardiovascular examination normal. Blood pressure 128/82.

Spirometry performed showing normal FEV1/FVC ratio, no evidence of obstruction.

Assessment and Plan:
Acute bronchitis most likely viral etiology. Symptomatic treatment recommended 
with rest, hydration, and over-the-counter cough suppressant. Patient instructed 
to return if symptoms worsen or persist beyond 7 days.

Hypertension stable, continue current medication regimen.

Follow-up in 2 weeks or as needed.

Electronically signed by Dr. Jane Smith, MD
NPI: 1234567890
Date: 10/15/2024
"""


def get_sample_medical_record():
    """Return sample medical record text"""
    return SAMPLE_MEDICAL_RECORD_TEXT


if __name__ == "__main__":
    print(SAMPLE_MEDICAL_RECORD_TEXT)
