"""
CMS-1500 PDF Generator
Generates a fillable PDF form for CMS-1500 claims matching the official CMS-1500 (02/12) layout.
"""

import io
import logging
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white, HexColor
from cms1500.schema import CMS1500Claim

logger = logging.getLogger(__name__)


class CMS1500PDFGenerator:
    """Generate CMS-1500 form as PDF matching official layout"""
    
    def __init__(self):
        self.page_width, self.page_height = letter
        # CMS-1500 form uses standard letter size with specific margins
        self.left_margin = 0.25 * inch
        self.top_margin = 0.25 * inch
        
    def generate_pdf(self, claim: CMS1500Claim) -> bytes:
        """
        Generate PDF bytes for CMS-1500 claim form.
        
        Args:
            claim: CMS1500Claim object
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Draw complete form structure
        self._draw_form_structure(c)
        
        # Fill in claim data
        self._fill_claim_data(c, claim)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_form_structure(self, c: canvas.Canvas):
        """Draw the complete CMS-1500 form structure with proper layout"""
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(self.page_width / 2, self.page_height - 0.4*inch, 
                           "CMS-1500 (02/12)")
        
        # Draw form boxes and lines
        y = self.page_height - 0.7*inch
        
        # Item 1: Type of Insurance (with boxes)
        c.setFont("Helvetica", 8)
        c.drawString(self.left_margin, y, "1.")
        checkbox_y = y - 0.05*inch
        checkbox_size = 0.12*inch
        
        insurance_types = [
            ("MEDICARE", 0.4*inch),
            ("MEDICAID", 1.0*inch),
            ("TRICARE", 1.6*inch),
            ("CHAMPVA", 2.2*inch),
            ("GROUP HEALTH PLAN", 2.8*inch),
            ("FECA", 4.0*inch),
            ("OTHER", 4.5*inch)
        ]
        
        for label, x_offset in insurance_types:
            c.rect(self.left_margin + x_offset, checkbox_y, checkbox_size, checkbox_size)
            c.drawString(self.left_margin + x_offset + 0.15*inch, y, label)
        
        # Item 1a: Insured's ID Number
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "1a. INSURED'S ID NUMBER")
        c.rect(self.left_margin + 1.6*inch, y - 0.15*inch, 2.8*inch, 0.2*inch)
        
        # Item 2: Patient's Name
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "2. PATIENT'S NAME (Last Name, First Name, Middle Initial)")
        c.rect(self.left_margin + 3.2*inch, y - 0.15*inch, 3.5*inch, 0.2*inch)
        
        # Item 3: Patient's Birth Date and Sex
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "3. PATIENT'S BIRTH DATE")
        c.rect(self.left_margin + 1.8*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.9*inch, y, "SEX")
        c.rect(self.left_margin + 3.2*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 3.25*inch, y, "M")
        c.rect(self.left_margin + 3.5*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 3.55*inch, y, "F")
        
        # Item 4: Insured's Name
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "4. INSURED'S NAME (If other than patient)")
        c.rect(self.left_margin + 3.2*inch, y - 0.15*inch, 3.5*inch, 0.2*inch)
        
        # Item 5: Patient's Address
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "5. PATIENT'S ADDRESS (No., Street)")
        c.rect(self.left_margin + 2.0*inch, y - 0.15*inch, 2.2*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.4*inch, y, "CITY")
        c.rect(self.left_margin + 4.8*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.9*inch, y, "STATE")
        c.rect(self.left_margin + 6.2*inch, y - 0.15*inch, 0.4*inch, 0.2*inch)
        c.drawString(self.left_margin + 6.7*inch, y, "ZIP")
        c.rect(self.left_margin + 7.0*inch, y - 0.15*inch, 0.7*inch, 0.2*inch)
        
        # Item 6: Patient Relationship to Insured
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "6. PATIENT RELATIONSHIP TO INSURED")
        c.rect(self.left_margin + 2.8*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.85*inch, y, "Self")
        c.rect(self.left_margin + 3.2*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 3.25*inch, y, "Spouse")
        c.rect(self.left_margin + 3.7*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 3.75*inch, y, "Child")
        c.rect(self.left_margin + 4.2*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.25*inch, y, "Other")
        
        # Item 7: Insured's Address
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "7. INSURED'S ADDRESS (No., Street)")
        c.rect(self.left_margin + 2.0*inch, y - 0.15*inch, 2.2*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.4*inch, y, "CITY")
        c.rect(self.left_margin + 4.8*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.9*inch, y, "STATE")
        c.rect(self.left_margin + 6.2*inch, y - 0.15*inch, 0.4*inch, 0.2*inch)
        c.drawString(self.left_margin + 6.7*inch, y, "ZIP")
        c.rect(self.left_margin + 7.0*inch, y - 0.15*inch, 0.7*inch, 0.2*inch)
        
        # Item 8: Reserved for NUCC
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "8. PATIENT STATUS")
        c.rect(self.left_margin + 1.8*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 1.85*inch, y, "Single")
        c.rect(self.left_margin + 2.4*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.45*inch, y, "Married")
        c.rect(self.left_margin + 3.1*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 3.15*inch, y, "Other")
        
        # Item 9-11: Other Insurance and Insured Info
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "9. OTHER INSURED'S NAME")
        c.rect(self.left_margin + 2.0*inch, y - 0.15*inch, 2.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.2*inch, y, "9a. OTHER INSURED'S POLICY OR GROUP NUMBER")
        c.rect(self.left_margin + 5.8*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "9b. RESERVED FOR NUCC USE")
        c.rect(self.left_margin + 2.0*inch, y - 0.15*inch, 2.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.2*inch, y, "9c. RESERVED FOR NUCC USE")
        c.rect(self.left_margin + 5.8*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "9d. INSURANCE PLAN NAME OR PROGRAM NAME")
        c.rect(self.left_margin + 3.0*inch, y - 0.15*inch, 4.3*inch, 0.2*inch)
        
        # Item 10-11: Condition and Insured Info
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "10. IS PATIENT'S CONDITION RELATED TO:")
        c.drawString(self.left_margin + 2.8*inch, y, "a. EMPLOYMENT (Current or Previous)")
        c.rect(self.left_margin + 5.2*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.25*inch, y, "Yes")
        c.rect(self.left_margin + 5.6*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.65*inch, y, "No")
        
        y -= 0.25*inch
        c.drawString(self.left_margin + 2.8*inch, y, "b. AUTO ACCIDENT")
        c.rect(self.left_margin + 4.0*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.05*inch, y, "Yes")
        c.rect(self.left_margin + 4.4*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.45*inch, y, "No")
        c.drawString(self.left_margin + 4.8*inch, y, "STATE")
        c.rect(self.left_margin + 5.2*inch, y - 0.15*inch, 0.4*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin + 2.8*inch, y, "c. OTHER ACCIDENT")
        c.rect(self.left_margin + 4.0*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.05*inch, y, "Yes")
        c.rect(self.left_margin + 4.4*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.45*inch, y, "No")
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "11. INSURED'S POLICY GROUP OR FECA NUMBER")
        c.rect(self.left_margin + 3.2*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        c.drawString(self.left_margin + 4.9*inch, y, "11a. INSURED'S DATE OF BIRTH")
        c.rect(self.left_margin + 6.2*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        c.drawString(self.left_margin + 7.2*inch, y, "SEX")
        c.rect(self.left_margin + 7.5*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 7.55*inch, y, "M")
        c.rect(self.left_margin + 7.7*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 7.75*inch, y, "F")
        
        # Item 12-13: Signatures
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "12. PATIENT'S OR AUTHORIZED PERSON'S SIGNATURE")
        c.rect(self.left_margin + 3.5*inch, y - 0.15*inch, 2.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.8*inch, y, "13. INSURED'S OR AUTHORIZED PERSON'S SIGNATURE")
        c.rect(self.left_margin + 6.5*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        
        # Item 14-19: Dates and Provider Info
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "14. DATE OF CURRENT ILLNESS, INJURY OR PREGNANCY (LMP)")
        c.rect(self.left_margin + 4.2*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "15. IF PATIENT HAS HAD SAME OR SIMILAR ILLNESS")
        c.drawString(self.left_margin + 3.5*inch, y, "15a. FIRST DATE")
        c.rect(self.left_margin + 4.2*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "16. DATES PATIENT UNABLE TO WORK IN CURRENT OCCUPATION")
        c.drawString(self.left_margin + 3.8*inch, y, "FROM")
        c.rect(self.left_margin + 4.2*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.2*inch, y, "TO")
        c.rect(self.left_margin + 5.4*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "17. NAME OF REFERRING PROVIDER OR OTHER SOURCE")
        c.rect(self.left_margin + 3.0*inch, y - 0.15*inch, 2.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.2*inch, y, "17a. NPI")
        c.rect(self.left_margin + 5.8*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "18. HOSPITALIZATION DATES RELATED TO CURRENT SERVICES")
        c.drawString(self.left_margin + 4.0*inch, y, "FROM")
        c.rect(self.left_margin + 4.4*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.4*inch, y, "TO")
        c.rect(self.left_margin + 5.6*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "19. RESERVED FOR LOCAL USE")
        c.rect(self.left_margin + 2.5*inch, y - 0.15*inch, 5.0*inch, 0.2*inch)
        
        # Item 20-23: Additional Info
        y -= 0.3*inch
        c.drawString(self.left_margin, y, "20. OUTSIDE LAB?")
        c.rect(self.left_margin + 1.5*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 1.55*inch, y, "Yes")
        c.rect(self.left_margin + 1.9*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 1.95*inch, y, "No")
        c.drawString(self.left_margin + 2.3*inch, y, "CHARGES $")
        c.rect(self.left_margin + 3.0*inch, y - 0.15*inch, 0.8*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "21. DIAGNOSIS OR NATURE OF ILLNESS OR INJURY (Relate items 24, E, F, G and H to the line number in 24E by letter)")
        c.rect(self.left_margin + 5.5*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.55*inch, y, "ICD-10-CM")
        c.rect(self.left_margin + 6.2*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 6.25*inch, y, "ICD-9-CM")
        
        # Diagnosis boxes A-L
        diag_y = y - 0.35*inch
        diag_x_start = self.left_margin
        for i, letter in enumerate('ABCDEFGHIJKL'):
            x_pos = diag_x_start + (i % 4) * 1.8*inch
            if i > 0 and i % 4 == 0:
                diag_y -= 0.25*inch
            c.drawString(x_pos, diag_y, f"{letter}.")
            c.rect(x_pos + 0.15*inch, diag_y - 0.15*inch, 1.2*inch, 0.2*inch)
        
        # Item 22-23
        y = diag_y - 0.4*inch
        c.drawString(self.left_margin, y, "22. RESUBMISSION CODE")
        c.rect(self.left_margin + 1.8*inch, y - 0.15*inch, 0.4*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.4*inch, y, "ORIGINAL REF. NO.")
        c.rect(self.left_margin + 3.5*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "23. PRIOR AUTHORIZATION NUMBER")
        c.rect(self.left_margin + 2.5*inch, y - 0.15*inch, 2.5*inch, 0.2*inch)
        
        # Item 24: Service Lines Table
        y -= 0.4*inch
        c.drawString(self.left_margin, y, "24. SERVICE LINES")
        
        # Service line headers
        header_y = y - 0.2*inch
        headers = [
            ("A", "DATE", 0.0),
            ("B", "POS", 0.8),
            ("C", "EMG", 1.1),
            ("D", "PROC", 1.4),
            ("E", "DIAG", 2.3),
            ("F", "CHARGES", 2.8),
            ("G", "DAYS", 3.5),
            ("H", "EPSDT", 3.8),
            ("I", "ID", 4.2),
            ("J", "REND", 4.6)
        ]
        
        for header, label, x_offset in headers:
            c.drawString(self.left_margin + x_offset*inch, header_y, header)
            c.drawString(self.left_margin + x_offset*inch, header_y - 0.15*inch, label)
        
        # Draw service line boxes (6 lines)
        line_height = 0.3*inch
        line_y_start = header_y - 0.35*inch
        
        for line_num in range(6):
            line_y = line_y_start - line_num * line_height
            
            # Draw horizontal line
            c.line(self.left_margin, line_y, self.left_margin + 7.5*inch, line_y)
            
            # Draw vertical dividers
            for x_offset in [0.8, 1.1, 1.4, 2.3, 2.8, 3.5, 3.8, 4.2, 4.6]:
                c.line(self.left_margin + x_offset*inch, line_y, 
                      self.left_margin + x_offset*inch, line_y + line_height)
        
        # Item 25-33: Provider and Billing Info
        y = line_y_start - 6 * line_height - 0.3*inch
        
        c.drawString(self.left_margin, y, "25. FEDERAL TAX I.D. NUMBER")
        c.rect(self.left_margin + 2.2*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.25*inch, y, "SSN")
        c.rect(self.left_margin + 2.7*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.75*inch, y, "EIN")
        c.rect(self.left_margin + 3.2*inch, y - 0.15*inch, 1.2*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "26. PATIENT'S ACCOUNT NO.")
        c.rect(self.left_margin + 2.2*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "27. ACCEPT ASSIGNMENT?")
        c.rect(self.left_margin + 2.0*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.05*inch, y, "Yes")
        c.rect(self.left_margin + 2.4*inch, y - 0.15*inch, 0.15*inch, 0.2*inch)
        c.drawString(self.left_margin + 2.45*inch, y, "No")
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "28. TOTAL CHARGE")
        c.rect(self.left_margin + 1.8*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 3.0*inch, y, "29. AMOUNT PAID")
        c.rect(self.left_margin + 4.2*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.4*inch, y, "30. BALANCE DUE")
        c.rect(self.left_margin + 6.2*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "31. SIGNATURE OF PHYSICIAN OR SUPPLIER (Include Degrees or Credentials)")
        c.rect(self.left_margin + 4.5*inch, y - 0.15*inch, 1.5*inch, 0.2*inch)
        c.drawString(self.left_margin + 6.2*inch, y, "DATE")
        c.rect(self.left_margin + 6.6*inch, y - 0.15*inch, 0.9*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "32. SERVICE FACILITY LOCATION INFORMATION")
        c.drawString(self.left_margin + 3.5*inch, y, "32a. NPI")
        c.rect(self.left_margin + 4.2*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.4*inch, y, "32b. OTHER ID #")
        c.rect(self.left_margin + 6.2*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        
        y -= 0.25*inch
        c.drawString(self.left_margin, y, "33. BILLING PROVIDER INFO & PH #")
        c.drawString(self.left_margin + 3.0*inch, y, "33a. NPI")
        c.rect(self.left_margin + 3.8*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
        c.drawString(self.left_margin + 5.0*inch, y, "33b. OTHER ID #")
        c.rect(self.left_margin + 5.8*inch, y - 0.15*inch, 1.0*inch, 0.2*inch)
    
    def _fill_claim_data(self, c: canvas.Canvas, claim: CMS1500Claim):
        """Fill in the claim data on the form with proper alignment"""
        c.setFont("Helvetica", 9)
        # Adjust baseline for text to align with box centers
        # Boxes are drawn at y - 0.15*inch with height 0.2*inch
        # Center of box is at y - 0.15 + 0.1 = y - 0.05*inch
        text_offset = -0.05*inch  # Offset to center text vertically in boxes
        
        y = self.page_height - 0.7*inch
        
        # Item 1: Type of Insurance (checkboxes)
        checkbox_y = y - 0.05*inch
        checkbox_size = 0.12*inch
        
        insurance_offsets = {
            'medicare': 0.4*inch,
            'medicaid': 1.0*inch,
            'tricare': 1.6*inch,
            'champva': 2.2*inch,
            'group_health': 2.8*inch,
            'feca': 4.0*inch,
            'other': 4.5*inch
        }
        
        if claim.insurance_type_medicare:
            c.rect(self.left_margin + insurance_offsets['medicare'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        if claim.insurance_type_medicaid:
            c.rect(self.left_margin + insurance_offsets['medicaid'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        if claim.insurance_type_tricare:
            c.rect(self.left_margin + insurance_offsets['tricare'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        if claim.insurance_type_champva:
            c.rect(self.left_margin + insurance_offsets['champva'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        if claim.insurance_type_group_health:
            c.rect(self.left_margin + insurance_offsets['group_health'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        if claim.insurance_type_feca:
            c.rect(self.left_margin + insurance_offsets['feca'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        if claim.insurance_type_other:
            c.rect(self.left_margin + insurance_offsets['other'], checkbox_y, checkbox_size, checkbox_size, fill=1)
        
        # Item 1a: Insured's ID Number
        y -= 0.25*inch
        c.drawString(self.left_margin + 1.65*inch, y + text_offset, claim.insured_id_number[:29])
        
        # Item 2: Patient's Name
        y -= 0.3*inch
        patient_name = f"{claim.patient_last_name}, {claim.patient_first_name}"
        if claim.patient_middle_initial:
            patient_name += f" {claim.patient_middle_initial}"
        c.drawString(self.left_margin + 3.25*inch, y + text_offset, patient_name[:35])
        
        # Item 3: Patient's Birth Date and Sex
        y -= 0.3*inch
        c.drawString(self.left_margin + 1.85*inch, y + text_offset, claim.patient_dob)
        if claim.patient_sex == "M":
            c.rect(self.left_margin + 3.25*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        elif claim.patient_sex == "F":
            c.rect(self.left_margin + 3.55*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        # Item 4: Insured's Name
        y -= 0.3*inch
        if claim.insured_name:
            c.drawString(self.left_margin + 3.25*inch, y + text_offset, claim.insured_name[:35])
        
        # Item 5: Patient's Address
        y -= 0.3*inch
        if claim.patient_address:
            c.drawString(self.left_margin + 2.05*inch, y + text_offset, claim.patient_address[:30])
        if claim.patient_city:
            c.drawString(self.left_margin + 4.85*inch, y + text_offset, claim.patient_city[:15])
        if claim.patient_state:
            c.drawString(self.left_margin + 6.25*inch, y + text_offset, claim.patient_state[:2])
        if claim.patient_zip:
            c.drawString(self.left_margin + 7.05*inch, y + text_offset, claim.patient_zip[:10])
        
        # Item 6: Patient Relationship
        y -= 0.3*inch
        if claim.patient_relationship_self:
            c.rect(self.left_margin + 2.85*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        elif claim.patient_relationship_spouse:
            c.rect(self.left_margin + 3.25*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        elif claim.patient_relationship_child:
            c.rect(self.left_margin + 3.75*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        elif claim.patient_relationship_other:
            c.rect(self.left_margin + 4.25*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        # Item 7: Insured's Address
        y -= 0.3*inch
        if claim.insured_address:
            c.drawString(self.left_margin + 2.05*inch, y + text_offset, claim.insured_address[:30])
        if claim.insured_city:
            c.drawString(self.left_margin + 4.85*inch, y + text_offset, claim.insured_city[:15])
        if claim.insured_state:
            c.drawString(self.left_margin + 6.25*inch, y + text_offset, claim.insured_state[:2])
        if claim.insured_zip:
            c.drawString(self.left_margin + 7.05*inch, y + text_offset, claim.insured_zip[:10])
        
        # Item 8: Patient Status
        y -= 0.3*inch
        if claim.patient_status_single:
            c.rect(self.left_margin + 1.85*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        elif hasattr(claim, 'patient_status_married') and claim.patient_status_married:
            c.rect(self.left_margin + 2.45*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        # Item 10: Condition Related To
        y -= 0.55*inch  # Skip item 9
        if claim.condition_related_employment:
            c.rect(self.left_margin + 5.25*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        else:
            c.rect(self.left_margin + 5.65*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        y -= 0.25*inch
        if claim.condition_related_auto_accident:
            c.rect(self.left_margin + 4.05*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
            if claim.auto_accident_state:
                c.drawString(self.left_margin + 5.25*inch, y + text_offset, claim.auto_accident_state[:2])
        else:
            c.rect(self.left_margin + 4.45*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        y -= 0.25*inch
        if claim.condition_related_other_accident:
            c.rect(self.left_margin + 4.05*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        else:
            c.rect(self.left_margin + 4.45*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        # Item 11: Policy Group Number
        y -= 0.25*inch
        if claim.insured_policy_group:
            c.drawString(self.left_margin + 3.25*inch, y + text_offset, claim.insured_policy_group[:20])
        
        # Item 12-13: Signatures
        y -= 0.3*inch
        if claim.patient_signature:
            c.drawString(self.left_margin + 3.55*inch, y + text_offset, claim.patient_signature[:25])
        if claim.insured_signature:
            c.drawString(self.left_margin + 6.55*inch, y + text_offset, claim.insured_signature[:20])
        
        # Item 14-19: Dates
        y -= 0.3*inch
        if claim.date_of_current_illness:
            c.drawString(self.left_margin + 4.25*inch, y + text_offset, claim.date_of_current_illness)
        
        y -= 0.25*inch
        if claim.other_date:
            c.drawString(self.left_margin + 4.25*inch, y + text_offset, claim.other_date)
        
        y -= 0.25*inch
        if claim.unable_to_work_from:
            c.drawString(self.left_margin + 4.25*inch, y + text_offset, claim.unable_to_work_from)
        if claim.unable_to_work_to:
            c.drawString(self.left_margin + 5.45*inch, y + text_offset, claim.unable_to_work_to)
        
        y -= 0.25*inch
        if claim.referring_provider_name:
            c.drawString(self.left_margin + 3.05*inch, y + text_offset, claim.referring_provider_name[:25])
        if claim.referring_provider_npi:
            c.drawString(self.left_margin + 5.85*inch, y + text_offset, claim.referring_provider_npi[:10])
        
        y -= 0.25*inch
        if claim.hospitalization_from:
            c.drawString(self.left_margin + 4.45*inch, y + text_offset, claim.hospitalization_from)
        if claim.hospitalization_to:
            c.drawString(self.left_margin + 5.65*inch, y + text_offset, claim.hospitalization_to)
        
        # Item 20: Outside Lab
        y -= 0.25*inch
        if claim.outside_lab:
            c.rect(self.left_margin + 1.55*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        else:
            c.rect(self.left_margin + 1.95*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        if claim.outside_lab_charges:
            c.drawString(self.left_margin + 3.05*inch, y + text_offset, f"${claim.outside_lab_charges:.2f}")
        
        # Item 21: Diagnosis codes (A-L) - center aligned in boxes
        y -= 0.25*inch
        diag_y = y - 0.35*inch
        diag_x_start = self.left_margin + 0.2*inch  # Start inside box
        
        for i, letter in enumerate('ABCDEFGHIJKL'):
            code = claim.get_diagnosis_by_letter(letter)
            if code:
                x_pos = diag_x_start + (i % 4) * 1.8*inch
                if i > 0 and i % 4 == 0:
                    diag_y -= 0.25*inch
                c.drawString(x_pos, diag_y + text_offset, code[:12])
        
        # Item 22-23
        y = diag_y - 0.4*inch
        if claim.resubmission_code:
            c.drawString(self.left_margin + 1.85*inch, y + text_offset, claim.resubmission_code[:1])
        if claim.original_ref_no:
            c.drawString(self.left_margin + 3.55*inch, y + text_offset, claim.original_ref_no[:20])
        
        y -= 0.25*inch
        if claim.prior_authorization_number:
            c.drawString(self.left_margin + 2.55*inch, y + text_offset, claim.prior_authorization_number[:25])
        
        # Item 24: Service Lines - format date as MM DD YY (2-digit year)
        # Column positions match the header positions exactly
        line_height = 0.3*inch
        line_y_start = y - 0.4*inch - 0.2*inch
        
        # Column start positions (matching header positions)
        col_a = 0.0*inch + 0.05*inch  # DATE
        col_b = 0.8*inch + 0.05*inch  # POS
        col_c = 1.1*inch + 0.05*inch  # EMG
        col_d = 1.4*inch + 0.05*inch  # PROC
        col_e = 2.3*inch + 0.05*inch  # DIAG
        col_f_start = 2.8*inch  # CHARGES (right-aligned)
        col_f_end = 3.5*inch
        col_g = 3.5*inch + 0.05*inch  # DAYS
        col_h = 3.8*inch + 0.05*inch  # EPSDT
        col_i = 4.2*inch + 0.05*inch  # ID
        col_j = 4.6*inch + 0.05*inch  # REND
        
        for idx, line in enumerate(claim.service_lines[:6]):
            line_y = line_y_start - idx * line_height
            
            # 24A: Date - convert to MM DD YY format
            date_str = line.date_from
            # If date is in MM DD YYYY format, convert to MM DD YY
            if len(date_str) >= 10:  # MM DD YYYY format
                parts = date_str.split()
                if len(parts) == 3:
                    year = parts[2]
                    if len(year) == 4:
                        year = year[-2:]  # Take last 2 digits
                    date_str = f"{parts[0]} {parts[1]} {year}"
            c.drawString(self.left_margin + col_a, line_y + text_offset, date_str[:8])
            
            # 24B: Place of Service
            c.drawString(self.left_margin + col_b, line_y + text_offset, line.place_of_service[:2])
            
            # 24C: EMG (if present)
            if line.emg:
                c.drawString(self.left_margin + col_c, line_y + text_offset, line.emg[:1])
            
            # 24D: CPT/HCPCS Code
            code_text = line.cpt_hcpcs
            if line.modifier1:
                code_text += f"-{line.modifier1}"
            if line.modifier2:
                code_text += f"-{line.modifier2}"
            c.drawString(self.left_margin + col_d, line_y + text_offset, code_text[:13])
            
            # 24E: Diagnosis Pointer
            c.drawString(self.left_margin + col_e, line_y + text_offset, line.diagnosis_pointer[:4])
            
            # 24F: Charges - right align within column (2.8 to 3.5)
            charge_str = f"${line.charges:.2f}"
            charge_width = c.stringWidth(charge_str, "Helvetica", 9)
            charge_x = self.left_margin + col_f_end - charge_width - 0.05*inch  # Right edge minus padding
            c.drawString(charge_x, line_y + text_offset, charge_str)
            
            # 24G: Days/Units
            days_str = str(line.days_or_units)
            c.drawString(self.left_margin + col_g, line_y + text_offset, days_str)
            
            # 24H: EPSDT (if present)
            if line.epsdt_family_plan:
                c.drawString(self.left_margin + col_h, line_y + text_offset, line.epsdt_family_plan[:1])
            
            # 24I: ID Qualifier (if present)
            if line.id_qualifier:
                c.drawString(self.left_margin + col_i, line_y + text_offset, line.id_qualifier[:2])
            
            # 24J: Rendering Provider
            if line.rendering_provider_id:
                c.drawString(self.left_margin + col_j, line_y + text_offset, line.rendering_provider_id[:10])
        
        # Item 25-33: Provider and Billing Info
        y = line_y_start - 6 * line_height - 0.3*inch
        
        # Item 25: Tax ID
        if claim.tax_id_type_ssn:
            c.rect(self.left_margin + 2.25*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        elif claim.tax_id_type_ein:
            c.rect(self.left_margin + 2.75*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        if claim.federal_tax_id:
            c.drawString(self.left_margin + 3.25*inch, y + text_offset, claim.federal_tax_id[:15])
        
        # Item 26: Patient Account Number
        y -= 0.25*inch
        if claim.patient_account_number:
            c.drawString(self.left_margin + 2.25*inch, y + text_offset, claim.patient_account_number[:15])
        
        # Item 27: Accept Assignment
        y -= 0.25*inch
        if claim.accept_assignment:
            c.rect(self.left_margin + 2.05*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        else:
            c.rect(self.left_margin + 2.45*inch, y - 0.15*inch, 0.12*inch, 0.15*inch, fill=1)
        
        # Item 28-30: Financial Totals - right align
        y -= 0.25*inch
        total_str = f"${claim.total_charge:.2f}"
        total_width = c.stringWidth(total_str, "Helvetica", 9)
        c.drawString(self.left_margin + 2.75*inch - total_width, y + text_offset, total_str)
        
        if claim.amount_paid:
            paid_str = f"${claim.amount_paid:.2f}"
            paid_width = c.stringWidth(paid_str, "Helvetica", 9)
            c.drawString(self.left_margin + 5.15*inch - paid_width, y + text_offset, paid_str)
        
        balance_str = f"${claim.balance_due:.2f}" if claim.balance_due else f"${claim.total_charge:.2f}"
        balance_width = c.stringWidth(balance_str, "Helvetica", 9)
        c.drawString(self.left_margin + 7.15*inch - balance_width, y + text_offset, balance_str)
        
        # Item 31: Physician Signature
        y -= 0.25*inch
        if claim.physician_signature:
            c.drawString(self.left_margin + 4.55*inch, y + text_offset, claim.physician_signature[:20])
        if claim.physician_signature_date:
            c.drawString(self.left_margin + 6.65*inch, y + text_offset, claim.physician_signature_date[:8])
        
        # Item 32: Service Facility
        y -= 0.25*inch
        if claim.service_facility_npi:
            c.drawString(self.left_margin + 4.25*inch, y + text_offset, claim.service_facility_npi[:10])
        if claim.service_facility_other_id:
            c.drawString(self.left_margin + 6.25*inch, y + text_offset, claim.service_facility_other_id[:15])
        
        # Item 33: Billing Provider
        y -= 0.25*inch
        if claim.billing_provider_npi:
            c.drawString(self.left_margin + 3.85*inch, y + text_offset, claim.billing_provider_npi[:10])
        if claim.billing_provider_other_id:
            c.drawString(self.left_margin + 5.85*inch, y + text_offset, claim.billing_provider_other_id[:15])


def generate_cms1500_pdf(claim: CMS1500Claim) -> bytes:
    """
    Convenience function to generate CMS-1500 PDF.
    
    Args:
        claim: CMS1500Claim object
        
    Returns:
        PDF file as bytes
    """
    generator = CMS1500PDFGenerator()
    return generator.generate_pdf(claim)
