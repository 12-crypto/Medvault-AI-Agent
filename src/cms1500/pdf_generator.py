"""
CMS-1500 PDF Generator
Generates a fillable PDF form for CMS-1500 claims matching the official CMS-1500 (02/12) layout.
Uses a field-based approach for precise text alignment.
"""

import io
import logging
from typing import Optional, Dict, Tuple, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white, lightgrey
from cms1500.schema import CMS1500Claim

logger = logging.getLogger(__name__)


class CMS1500PDFGenerator:
    """Generate CMS-1500 form as PDF matching official layout"""
    
    def __init__(self):
        self.page_width, self.page_height = letter  # 8.5 x 11 inches
        self.left_margin = 0.3 * inch
        self.right_margin = self.page_width - 0.3 * inch
        self.top_margin = self.page_height - 0.4 * inch
        
        # Standard row height for form fields
        self.row_height = 0.22 * inch
        self.field_padding = 0.03 * inch
        
    def generate_pdf(self, claim: CMS1500Claim) -> bytes:
        """Generate PDF bytes for CMS-1500 claim form."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Draw form with data
        self._draw_complete_form(c, claim)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_field_box(self, c: canvas.Canvas, x: float, y: float, 
                        width: float, height: float, label: str = None,
                        value: str = None, align: str = 'left',
                        draw_box: bool = True, font_size: int = 8):
        """Draw a field box with optional label and value."""
        
        # Draw box outline
        if draw_box:
            c.setStrokeColor(black)
            c.setLineWidth(0.5)
            c.rect(x, y, width, height)
        
        # Draw label (small, above the value)
        if label:
            c.setFont("Helvetica", 6)
            c.setFillColor(black)
            c.drawString(x + self.field_padding, y + height - 8, label)
        
        # Draw value
        if value:
            c.setFont("Helvetica", font_size)
            c.setFillColor(black)
            
            # Calculate text position
            text_y = y + self.field_padding + 2
            
            # Truncate if too long
            available_width = width - 2 * self.field_padding
            while value and c.stringWidth(value, "Helvetica", font_size) > available_width:
                value = value[:-1]
            
            if value:
                text_width = c.stringWidth(value, "Helvetica", font_size)
                if align == 'left':
                    text_x = x + self.field_padding
                elif align == 'right':
                    text_x = x + width - self.field_padding - text_width
                else:  # center
                    text_x = x + (width - text_width) / 2
                
                c.drawString(text_x, text_y, value)
    
    def _draw_checkbox(self, c: canvas.Canvas, x: float, y: float, 
                       checked: bool = False, size: float = 0.1 * inch):
        """Draw a checkbox."""
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.rect(x, y, size, size)
        
        if checked:
            c.setFillColor(black)
            c.rect(x + 2, y + 2, size - 4, size - 4, fill=1)
    
    def _draw_complete_form(self, c: canvas.Canvas, claim: CMS1500Claim):
        """Draw the complete CMS-1500 form with data."""
        
        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.page_width / 2, self.top_margin, "CMS-1500 (02/12)")
        
        y = self.top_margin - 0.35 * inch
        
        # ===== ROW 1: Insurance Type =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y, "1.")
        
        checkbox_y = y - 3
        checkbox_size = 0.1 * inch
        insurance_items = [
            ("MEDICARE", claim.insurance_type_medicare, 0.3),
            ("MEDICAID", claim.insurance_type_medicaid, 1.1),
            ("TRICARE", claim.insurance_type_tricare, 1.9),
            ("CHAMPVA", claim.insurance_type_champva, 2.6),
            ("GROUP HEALTH", claim.insurance_type_group_health, 3.4),
            ("FECA", claim.insurance_type_feca, 4.4),
            ("OTHER", claim.insurance_type_other, 5.0)
        ]
        
        for label, checked, x_offset in insurance_items:
            self._draw_checkbox(c, self.left_margin + x_offset * inch, checkbox_y, checked, checkbox_size)
            c.setFont("Helvetica", 6)
            c.drawString(self.left_margin + x_offset * inch + checkbox_size + 2, y, label)
        
        y -= self.row_height + 0.05 * inch
        
        # ===== ROW 2: Insured's ID Number =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "1a. INSURED'S I.D. NUMBER")
        self._draw_field_box(c, self.left_margin + 1.8 * inch, y - self.row_height + 5, 
                            2.5 * inch, self.row_height, value=claim.insured_id_number)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 3: Patient's Name =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "2. PATIENT'S NAME (Last, First, MI)")
        patient_name = f"{claim.patient_last_name}, {claim.patient_first_name}"
        if claim.patient_middle_initial:
            patient_name += f" {claim.patient_middle_initial}"
        self._draw_field_box(c, self.left_margin + 2.5 * inch, y - self.row_height + 5,
                            3.0 * inch, self.row_height, value=patient_name)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 4: Patient's Birth Date and Sex =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "3. PATIENT'S BIRTH DATE")
        self._draw_field_box(c, self.left_margin + 1.8 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.patient_dob)
        
        c.drawString(self.left_margin + 3.2 * inch, y + 5, "SEX")
        # M checkbox
        self._draw_checkbox(c, self.left_margin + 3.5 * inch, y - 5, claim.patient_sex == "M")
        c.drawString(self.left_margin + 3.65 * inch, y + 2, "M")
        # F checkbox
        self._draw_checkbox(c, self.left_margin + 3.9 * inch, y - 5, claim.patient_sex == "F")
        c.drawString(self.left_margin + 4.05 * inch, y + 2, "F")
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 5: Insured's Name =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "4. INSURED'S NAME")
        self._draw_field_box(c, self.left_margin + 1.5 * inch, y - self.row_height + 5,
                            2.5 * inch, self.row_height, value=claim.insured_name or "Self")
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 6: Patient's Address =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "5. PATIENT'S ADDRESS")
        
        # Street
        self._draw_field_box(c, self.left_margin + 1.6 * inch, y - self.row_height + 5,
                            2.0 * inch, self.row_height, value=claim.patient_address)
        
        # City
        c.drawString(self.left_margin + 3.8 * inch, y + 5, "CITY")
        self._draw_field_box(c, self.left_margin + 4.2 * inch, y - self.row_height + 5,
                            1.3 * inch, self.row_height, value=claim.patient_city)
        
        # State
        c.drawString(self.left_margin + 5.6 * inch, y + 5, "ST")
        self._draw_field_box(c, self.left_margin + 5.85 * inch, y - self.row_height + 5,
                            0.4 * inch, self.row_height, value=claim.patient_state, align='center')
        
        # ZIP
        c.drawString(self.left_margin + 6.35 * inch, y + 5, "ZIP")
        self._draw_field_box(c, self.left_margin + 6.6 * inch, y - self.row_height + 5,
                            0.8 * inch, self.row_height, value=claim.patient_zip)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 7: Patient Relationship =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "6. PATIENT RELATIONSHIP TO INSURED")
        
        rel_items = [
            ("Self", claim.patient_relationship_self, 2.8),
            ("Spouse", claim.patient_relationship_spouse, 3.4),
            ("Child", claim.patient_relationship_child, 4.1),
            ("Other", claim.patient_relationship_other, 4.7)
        ]
        
        for label, checked, x_offset in rel_items:
            self._draw_checkbox(c, self.left_margin + x_offset * inch, y - 5, checked)
            c.drawString(self.left_margin + x_offset * inch + 0.12 * inch, y + 2, label)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 8: Insured's Address =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "7. INSURED'S ADDRESS")
        
        # Street
        self._draw_field_box(c, self.left_margin + 1.6 * inch, y - self.row_height + 5,
                            2.0 * inch, self.row_height, value=claim.insured_address)
        
        # City
        c.drawString(self.left_margin + 3.8 * inch, y + 5, "CITY")
        self._draw_field_box(c, self.left_margin + 4.2 * inch, y - self.row_height + 5,
                            1.3 * inch, self.row_height, value=claim.insured_city)
        
        # State
        c.drawString(self.left_margin + 5.6 * inch, y + 5, "ST")
        self._draw_field_box(c, self.left_margin + 5.85 * inch, y - self.row_height + 5,
                            0.4 * inch, self.row_height, value=claim.insured_state, align='center')
        
        # ZIP
        c.drawString(self.left_margin + 6.35 * inch, y + 5, "ZIP")
        self._draw_field_box(c, self.left_margin + 6.6 * inch, y - self.row_height + 5,
                            0.8 * inch, self.row_height, value=claim.insured_zip)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 9: Patient Status =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "8. PATIENT STATUS")
        
        status_items = [
            ("Single", claim.patient_status_single, 1.5),
            ("Married", claim.patient_status_married, 2.2),
            ("Other", claim.patient_status_other, 3.0)
        ]
        
        for label, checked, x_offset in status_items:
            self._draw_checkbox(c, self.left_margin + x_offset * inch, y - 5, checked)
            c.drawString(self.left_margin + x_offset * inch + 0.12 * inch, y + 2, label)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 10: Other Insured's Name =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "9. OTHER INSURED'S NAME")
        self._draw_field_box(c, self.left_margin + 1.8 * inch, y - self.row_height + 5,
                            2.0 * inch, self.row_height, value=claim.other_insured_name)
        
        c.drawString(self.left_margin + 4.0 * inch, y + 5, "9a. OTHER INSURED'S POLICY OR GROUP NUMBER")
        self._draw_field_box(c, self.left_margin + 6.3 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.other_insured_policy)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 11: Reserved =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "9b. RESERVED FOR NUCC USE")
        self._draw_field_box(c, self.left_margin + 1.8 * inch, y - self.row_height + 5,
                            2.0 * inch, self.row_height)
        
        c.drawString(self.left_margin + 4.0 * inch, y + 5, "9c. RESERVED FOR NUCC USE")
        self._draw_field_box(c, self.left_margin + 6.3 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 12: Insurance Plan Name =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "9d. INSURANCE PLAN NAME OR PROGRAM NAME")
        self._draw_field_box(c, self.left_margin + 3.2 * inch, y - self.row_height + 5,
                            4.3 * inch, self.row_height, value=claim.other_insurance_plan_name)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 13: Condition Related To =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "10. IS PATIENT'S CONDITION RELATED TO:")
        
        # Employment
        c.drawString(self.left_margin + 2.5 * inch, y + 5, "a. EMPLOYMENT")
        self._draw_checkbox(c, self.left_margin + 3.8 * inch, y - 5, claim.condition_related_employment == True)
        c.drawString(self.left_margin + 3.95 * inch, y + 2, "Yes")
        self._draw_checkbox(c, self.left_margin + 4.3 * inch, y - 5, claim.condition_related_employment == False)
        c.drawString(self.left_margin + 4.45 * inch, y + 2, "No")
        
        y -= self.row_height + 0.04 * inch
        
        # Auto Accident
        c.drawString(self.left_margin + 2.5 * inch, y + 5, "b. AUTO ACCIDENT")
        self._draw_checkbox(c, self.left_margin + 3.8 * inch, y - 5, claim.condition_related_auto_accident == True)
        c.drawString(self.left_margin + 3.95 * inch, y + 2, "Yes")
        self._draw_checkbox(c, self.left_margin + 4.3 * inch, y - 5, claim.condition_related_auto_accident == False)
        c.drawString(self.left_margin + 4.45 * inch, y + 2, "No")
        
        c.drawString(self.left_margin + 4.9 * inch, y + 5, "STATE")
        self._draw_field_box(c, self.left_margin + 5.3 * inch, y - self.row_height + 5,
                            0.5 * inch, self.row_height, value=claim.auto_accident_state, align='center')
        
        y -= self.row_height + 0.04 * inch
        
        # Other Accident
        c.drawString(self.left_margin + 2.5 * inch, y + 5, "c. OTHER ACCIDENT")
        self._draw_checkbox(c, self.left_margin + 3.8 * inch, y - 5, claim.condition_related_other_accident == True)
        c.drawString(self.left_margin + 3.95 * inch, y + 2, "Yes")
        self._draw_checkbox(c, self.left_margin + 4.3 * inch, y - 5, claim.condition_related_other_accident == False)
        c.drawString(self.left_margin + 4.45 * inch, y + 2, "No")
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 14: Insured's Policy Group =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "11. INSURED'S POLICY GROUP OR FECA NUMBER")
        self._draw_field_box(c, self.left_margin + 3.2 * inch, y - self.row_height + 5,
                            1.5 * inch, self.row_height, value=claim.insured_policy_group)
        
        c.drawString(self.left_margin + 5.0 * inch, y + 5, "11a. INSURED'S DATE OF BIRTH")
        self._draw_field_box(c, self.left_margin + 6.5 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=claim.insured_dob)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 15: Signatures =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "12. PATIENT'S OR AUTHORIZED PERSON'S SIGNATURE")
        self._draw_field_box(c, self.left_margin + 3.2 * inch, y - self.row_height + 5,
                            1.8 * inch, self.row_height, value=claim.patient_signature)
        
        c.drawString(self.left_margin + 5.2 * inch, y + 5, "13. INSURED'S SIGNATURE")
        self._draw_field_box(c, self.left_margin + 6.3 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.insured_signature)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 16: Date of Illness =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "14. DATE OF CURRENT ILLNESS, INJURY OR PREGNANCY (LMP)")
        self._draw_field_box(c, self.left_margin + 4.0 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.date_of_current_illness)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 17: Similar Illness =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "15. IF PATIENT HAS HAD SAME OR SIMILAR ILLNESS")
        c.drawString(self.left_margin + 3.2 * inch, y + 5, "FIRST DATE")
        self._draw_field_box(c, self.left_margin + 4.0 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.other_date)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 18: Unable to Work =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "16. DATES PATIENT UNABLE TO WORK IN CURRENT OCCUPATION")
        c.drawString(self.left_margin + 3.6 * inch, y + 5, "FROM")
        self._draw_field_box(c, self.left_margin + 4.0 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=claim.unable_to_work_from)
        c.drawString(self.left_margin + 5.2 * inch, y + 5, "TO")
        self._draw_field_box(c, self.left_margin + 5.5 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=claim.unable_to_work_to)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 19: Referring Provider =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "17. NAME OF REFERRING PROVIDER OR OTHER SOURCE")
        self._draw_field_box(c, self.left_margin + 3.4 * inch, y - self.row_height + 5,
                            1.8 * inch, self.row_height, value=claim.referring_provider_name)
        c.drawString(self.left_margin + 5.4 * inch, y + 5, "17a. NPI")
        self._draw_field_box(c, self.left_margin + 5.9 * inch, y - self.row_height + 5,
                            1.5 * inch, self.row_height, value=claim.referring_provider_npi)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 20: Hospitalization Dates =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "18. HOSPITALIZATION DATES RELATED TO CURRENT SERVICES")
        c.drawString(self.left_margin + 3.6 * inch, y + 5, "FROM")
        self._draw_field_box(c, self.left_margin + 4.0 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=claim.hospitalization_from)
        c.drawString(self.left_margin + 5.2 * inch, y + 5, "TO")
        self._draw_field_box(c, self.left_margin + 5.5 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=claim.hospitalization_to)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 21: Reserved for Local Use =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "19. RESERVED FOR LOCAL USE")
        self._draw_field_box(c, self.left_margin + 2.0 * inch, y - self.row_height + 5,
                            5.5 * inch, self.row_height, value=claim.additional_claim_info)
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 22: Outside Lab =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "20. OUTSIDE LAB?")
        self._draw_checkbox(c, self.left_margin + 1.2 * inch, y - 5, claim.outside_lab == True)
        c.drawString(self.left_margin + 1.35 * inch, y + 2, "Yes")
        self._draw_checkbox(c, self.left_margin + 1.7 * inch, y - 5, claim.outside_lab == False)
        c.drawString(self.left_margin + 1.85 * inch, y + 2, "No")
        
        c.drawString(self.left_margin + 2.3 * inch, y + 5, "$ CHARGES")
        charges_str = f"${claim.outside_lab_charges:.2f}" if claim.outside_lab_charges else ""
        self._draw_field_box(c, self.left_margin + 3.0 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=charges_str, align='right')
        
        y -= self.row_height + 0.08 * inch
        
        # ===== ROW 23: Diagnosis Codes =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "21. DIAGNOSIS OR NATURE OF ILLNESS OR INJURY")
        
        # ICD indicator
        c.drawString(self.left_margin + 4.0 * inch, y + 5, "ICD Ind.")
        self._draw_checkbox(c, self.left_margin + 4.6 * inch, y - 5, claim.icd_indicator.value == "0")
        c.drawString(self.left_margin + 4.75 * inch, y + 2, "ICD-10")
        self._draw_checkbox(c, self.left_margin + 5.3 * inch, y - 5, claim.icd_indicator.value == "9")
        c.drawString(self.left_margin + 5.45 * inch, y + 2, "ICD-9")
        
        y -= self.row_height + 0.05 * inch
        
        # Diagnosis boxes A-L (4 columns x 3 rows)
        diag_box_width = 1.6 * inch
        diag_box_height = self.row_height
        
        for row in range(3):
            for col in range(4):
                idx = row * 4 + col
                letter = 'ABCDEFGHIJKL'[idx]
                x = self.left_margin + col * (diag_box_width + 0.1 * inch)
                code = claim.get_diagnosis_by_letter(letter)
                c.setFont("Helvetica", 7)
                c.drawString(x, y + 5, f"{letter}.")
                self._draw_field_box(c, x + 0.15 * inch, y - diag_box_height + 5,
                                    diag_box_width - 0.2 * inch, diag_box_height, value=code)
            y -= diag_box_height + 0.04 * inch
        
        y -= 0.05 * inch
        
        # ===== ROW 24: Resubmission Code =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "22. RESUBMISSION CODE")
        self._draw_field_box(c, self.left_margin + 1.5 * inch, y - self.row_height + 5,
                            0.5 * inch, self.row_height, value=claim.resubmission_code, align='center')
        
        c.drawString(self.left_margin + 2.2 * inch, y + 5, "ORIGINAL REF. NO.")
        self._draw_field_box(c, self.left_margin + 3.3 * inch, y - self.row_height + 5,
                            1.5 * inch, self.row_height, value=claim.original_ref_no)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW 25: Prior Authorization =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "23. PRIOR AUTHORIZATION NUMBER")
        self._draw_field_box(c, self.left_margin + 2.3 * inch, y - self.row_height + 5,
                            2.5 * inch, self.row_height, value=claim.prior_authorization_number)
        
        y -= self.row_height + 0.1 * inch
        
        # ===== SERVICE LINES TABLE =====
        c.setFont("Helvetica-Bold", 7)
        c.drawString(self.left_margin, y + 5, "24. SERVICE LINES")
        
        y -= 0.15 * inch
        
        # Table headers
        headers = [
            ("A. DATE(S) OF SERVICE", 0, 0.9),
            ("B. POS", 0.95, 0.3),
            ("C. EMG", 1.3, 0.25),
            ("D. PROCEDURES/SERVICES", 1.6, 1.0),
            ("E. DX", 2.65, 0.35),
            ("F. $ CHARGES", 3.05, 0.7),
            ("G. DAYS", 3.8, 0.35),
            ("H. EPSDT", 4.2, 0.35),
            ("I. ID", 4.6, 0.3),
            ("J. RENDERING", 4.95, 0.7)
        ]
        
        c.setFont("Helvetica", 6)
        for label, x_offset, width in headers:
            c.drawString(self.left_margin + x_offset * inch, y + 3, label)
        
        y -= 0.12 * inch
        
        # Draw header line
        c.setLineWidth(0.5)
        c.line(self.left_margin, y, self.left_margin + 7.5 * inch, y)
        
        # Service lines
        line_height = 0.25 * inch
        
        for idx, line in enumerate(claim.service_lines[:6]):
            line_y = y - (idx + 1) * line_height
            
            # Draw row separator
            c.line(self.left_margin, line_y, self.left_margin + 7.5 * inch, line_y)
            
            c.setFont("Helvetica", 8)
            
            # Format date
            date_str = line.date_from
            if len(date_str) >= 10:
                parts = date_str.split()
                if len(parts) == 3 and len(parts[2]) == 4:
                    date_str = f"{parts[0]} {parts[1]} {parts[2][-2:]}"
            
            # A: Date
            c.drawString(self.left_margin + 0.02 * inch, line_y + 7, date_str[:10])
            
            # B: POS
            c.drawString(self.left_margin + 1.0 * inch, line_y + 7, line.place_of_service)
            
            # C: EMG
            if line.emg:
                c.drawString(self.left_margin + 1.35 * inch, line_y + 7, line.emg)
            
            # D: Procedure
            proc_text = line.cpt_hcpcs
            if line.modifier1:
                proc_text += f"-{line.modifier1}"
            c.drawString(self.left_margin + 1.65 * inch, line_y + 7, proc_text)
            
            # E: Diagnosis Pointer
            c.drawString(self.left_margin + 2.7 * inch, line_y + 7, line.diagnosis_pointer)
            
            # F: Charges (right-aligned)
            charge_str = f"${line.charges:.2f}"
            charge_width = c.stringWidth(charge_str, "Helvetica", 8)
            c.drawString(self.left_margin + 3.7 * inch - charge_width, line_y + 7, charge_str)
            
            # G: Days
            c.drawString(self.left_margin + 3.85 * inch, line_y + 7, str(line.days_or_units))
            
            # H: EPSDT
            if line.epsdt_family_plan:
                c.drawString(self.left_margin + 4.25 * inch, line_y + 7, line.epsdt_family_plan)
            
            # I: ID Qualifier
            if line.id_qualifier:
                c.drawString(self.left_margin + 4.65 * inch, line_y + 7, line.id_qualifier)
            
            # J: Rendering Provider
            if line.rendering_provider_id:
                c.drawString(self.left_margin + 5.0 * inch, line_y + 7, line.rendering_provider_id[:10])
        
        # Draw remaining empty lines
        for idx in range(len(claim.service_lines), 6):
            line_y = y - (idx + 1) * line_height
            c.line(self.left_margin, line_y, self.left_margin + 7.5 * inch, line_y)
        
        y = y - 6 * line_height - 0.15 * inch
        
        # ===== BOTTOM SECTION =====
        
        # ===== ROW: Federal Tax ID =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "25. FEDERAL TAX I.D. NUMBER")
        self._draw_checkbox(c, self.left_margin + 1.8 * inch, y - 5, claim.tax_id_type_ssn)
        c.drawString(self.left_margin + 1.95 * inch, y + 2, "SSN")
        self._draw_checkbox(c, self.left_margin + 2.3 * inch, y - 5, claim.tax_id_type_ein)
        c.drawString(self.left_margin + 2.45 * inch, y + 2, "EIN")
        self._draw_field_box(c, self.left_margin + 2.9 * inch, y - self.row_height + 5,
                            1.5 * inch, self.row_height, value=claim.federal_tax_id)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW: Patient Account Number =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "26. PATIENT'S ACCOUNT NO.")
        self._draw_field_box(c, self.left_margin + 1.8 * inch, y - self.row_height + 5,
                            1.5 * inch, self.row_height, value=claim.patient_account_number)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW: Accept Assignment =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "27. ACCEPT ASSIGNMENT?")
        self._draw_checkbox(c, self.left_margin + 1.7 * inch, y - 5, claim.accept_assignment == True)
        c.drawString(self.left_margin + 1.85 * inch, y + 2, "Yes")
        self._draw_checkbox(c, self.left_margin + 2.2 * inch, y - 5, claim.accept_assignment == False)
        c.drawString(self.left_margin + 2.35 * inch, y + 2, "No")
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW: Total Charge, Amount Paid, Balance Due =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "28. TOTAL CHARGE")
        total_str = f"${claim.total_charge:.2f}"
        self._draw_field_box(c, self.left_margin + 1.3 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=total_str, align='right')
        
        c.drawString(self.left_margin + 2.5 * inch, y + 5, "29. AMOUNT PAID")
        paid_str = f"${claim.amount_paid:.2f}" if claim.amount_paid else "$0.00"
        self._draw_field_box(c, self.left_margin + 3.6 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=paid_str, align='right')
        
        c.drawString(self.left_margin + 4.8 * inch, y + 5, "30. BALANCE DUE")
        balance_str = f"${claim.balance_due:.2f}" if claim.balance_due else total_str
        self._draw_field_box(c, self.left_margin + 5.9 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=balance_str, align='right')
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW: Physician Signature =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "31. SIGNATURE OF PHYSICIAN OR SUPPLIER")
        self._draw_field_box(c, self.left_margin + 2.8 * inch, y - self.row_height + 5,
                            1.8 * inch, self.row_height, value=claim.physician_signature)
        
        c.drawString(self.left_margin + 4.8 * inch, y + 5, "DATE")
        self._draw_field_box(c, self.left_margin + 5.2 * inch, y - self.row_height + 5,
                            1.0 * inch, self.row_height, value=claim.physician_signature_date)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW: Service Facility =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "32. SERVICE FACILITY LOCATION INFORMATION")
        c.drawString(self.left_margin + 3.2 * inch, y + 5, "32a. NPI")
        self._draw_field_box(c, self.left_margin + 3.6 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.service_facility_npi)
        
        c.drawString(self.left_margin + 5.0 * inch, y + 5, "32b. OTHER ID")
        self._draw_field_box(c, self.left_margin + 5.7 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.service_facility_other_id)
        
        y -= self.row_height + 0.06 * inch
        
        # ===== ROW: Billing Provider =====
        c.setFont("Helvetica", 7)
        c.drawString(self.left_margin, y + 5, "33. BILLING PROVIDER INFO & PH #")
        c.drawString(self.left_margin + 2.5 * inch, y + 5, "33a. NPI")
        self._draw_field_box(c, self.left_margin + 3.0 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.billing_provider_npi)
        
        c.drawString(self.left_margin + 4.4 * inch, y + 5, "33b. OTHER ID")
        self._draw_field_box(c, self.left_margin + 5.2 * inch, y - self.row_height + 5,
                            1.2 * inch, self.row_height, value=claim.billing_provider_other_id)


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
