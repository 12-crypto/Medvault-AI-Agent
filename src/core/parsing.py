"""
Document Parsing Module
Handles parsing of various document formats (PDF, text, images)
and preprocesses them for data extraction.
"""

import logging
from pathlib import Path
from typing import Union, Optional, Dict, Any
import re

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from core.ocr import OCREngine, extract_text_from_file

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Parse various document formats and extract structured content.
    
    Supports:
    - PDF (text and scanned)
    - Plain text
    - Images (via OCR)
    """
    
    def __init__(self, use_ocr: bool = True):
        """
        Initialize parser.
        
        Args:
            use_ocr: Enable OCR for scanned documents
        """
        self.use_ocr = use_ocr
        self.ocr_engine = OCREngine() if use_ocr else None
        
    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse document and extract content.
        
        Args:
            file_path: Path to document
            
        Returns:
            Dictionary with parsed content and metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        logger.info(f"Parsing document: {path.name}")
        
        # Route to appropriate parser
        if path.suffix.lower() == '.pdf':
            return self._parse_pdf(path)
        elif path.suffix.lower() in ['.txt', '.text']:
            return self._parse_text(path)
        elif path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self._parse_image(path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    def _parse_pdf(self, path: Path) -> Dict[str, Any]:
        """Parse PDF document"""
        
        # Try text extraction first (faster)
        text = self._extract_pdf_text(path)
        
        # If minimal text found, use OCR
        if not text or len(text.strip()) < 100:
            logger.info("Minimal text in PDF, using OCR")
            if self.use_ocr:
                ocr_result = self.ocr_engine.process_document(path)
                text = ocr_result.text
                extraction_method = "ocr"
            else:
                extraction_method = "text_extraction_failed"
        else:
            extraction_method = "text_extraction"
        
        # Extract metadata
        metadata = self._extract_pdf_metadata(path)
        
        return {
            "text": text,
            "type": "pdf",
            "extraction_method": extraction_method,
            "metadata": metadata,
            "file_name": path.name,
            "file_size": path.stat().st_size
        }
    
    def _extract_pdf_text(self, path: Path) -> str:
        """Extract text from PDF using available libraries"""
        
        text_parts = []
        
        # Try pdfplumber first (better for forms/tables)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                logger.debug("Extracted text with pdfplumber")
                return "\n\n".join(text_parts)
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                logger.debug("Extracted text with PyPDF2")
                return "\n\n".join(text_parts)
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
        
        return ""
    
    def _extract_pdf_metadata(self, path: Path) -> Dict[str, Any]:
        """Extract PDF metadata"""
        
        metadata = {}
        
        if PYPDF2_AVAILABLE:
            try:
                with open(path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    info = reader.metadata
                    
                    if info:
                        metadata = {
                            "title": info.get("/Title", ""),
                            "author": info.get("/Author", ""),
                            "subject": info.get("/Subject", ""),
                            "creator": info.get("/Creator", ""),
                            "producer": info.get("/Producer", ""),
                            "creation_date": info.get("/CreationDate", ""),
                        }
                    
                    metadata["pages"] = len(reader.pages)
            except Exception as e:
                logger.warning(f"Could not extract PDF metadata: {e}")
        
        return metadata
    
    def _parse_text(self, path: Path) -> Dict[str, Any]:
        """Parse plain text file"""
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()
        
        return {
            "text": text,
            "type": "text",
            "extraction_method": "direct",
            "metadata": {},
            "file_name": path.name,
            "file_size": path.stat().st_size
        }
    
    def _parse_image(self, path: Path) -> Dict[str, Any]:
        """Parse image file with OCR"""
        
        if not self.use_ocr:
            raise RuntimeError("OCR disabled but required for image processing")
        
        ocr_result = self.ocr_engine.process_document(path)
        
        return {
            "text": ocr_result.text,
            "type": "image",
            "extraction_method": "ocr",
            "metadata": {
                "ocr_engine": ocr_result.engine,
                "pages": ocr_result.pages,
                "blocks": len(ocr_result.blocks)
            },
            "file_name": path.name,
            "file_size": path.stat().st_size
        }


class TextCleaner:
    """Clean and normalize extracted text"""
    
    @staticmethod
    def clean(text: str) -> str:
        """
        Clean extracted text.
        
        - Remove excessive whitespace
        - Normalize line breaks
        - Fix common OCR artifacts
        """
        
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix common OCR mistakes
        text = text.replace('|', 'I')  # Common OCR error
        text = text.replace('~', '-')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_lines(text: str) -> list:
        """Split text into lines and filter empty ones"""
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    @staticmethod
    def find_sections(text: str, patterns: Dict[str, str]) -> Dict[str, str]:
        """
        Find sections in text based on regex patterns.
        
        Args:
            text: Source text
            patterns: Dict of {section_name: regex_pattern}
            
        Returns:
            Dict of {section_name: extracted_text}
        """
        sections = {}
        
        for name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                sections[name] = match.group(0)
        
        return sections


def parse_document(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to parse a document.
    
    Args:
        file_path: Path to document
        
    Returns:
        Parsed document dictionary
    """
    parser = DocumentParser(use_ocr=True)
    result = parser.parse(file_path)
    
    # Clean text
    result["text"] = TextCleaner.clean(result["text"])
    
    return result
