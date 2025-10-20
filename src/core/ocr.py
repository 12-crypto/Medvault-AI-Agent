"""
OCR Engine Module
Handles text extraction from images and scanned documents using Tesseract OCR
with optional Llama Vision fallback for enhanced structure recognition.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union, List
import io

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available. OCR will be limited.")

from pdf2image import convert_from_path, convert_from_bytes

logger = logging.getLogger(__name__)


class OCREngine(str, Enum):
    """Available OCR engines"""
    TESSERACT = "tesseract"
    LLAMA_VISION = "llama_vision"
    AUTO = "auto"


@dataclass
class DocumentBlock:
    """Represents a block of text extracted from a document"""
    text: str
    page: int
    confidence: float
    bbox: Optional[tuple] = None  # (x1, y1, x2, y2)
    block_type: str = "text"  # text, table, heading, etc.


@dataclass
class OCRResult:
    """Result of OCR processing"""
    text: str
    blocks: List[DocumentBlock]
    pages: int
    engine: str
    metadata: dict


class OCREngine:
    """
    Multi-modal OCR engine supporting Tesseract and Llama Vision.
    
    Tesseract is used for fast, accurate text extraction.
    Llama Vision (via Ollama) can be used as fallback for:
    - Low quality images
    - Complex layouts
    - Table structure detection
    - Handwritten text hints
    """
    
    def __init__(
        self,
        engine: str = "auto",
        tesseract_cmd: Optional[str] = None,
        use_vision_fallback: bool = True
    ):
        """
        Initialize OCR engine.
        
        Args:
            engine: OCR engine to use (tesseract, llama_vision, auto)
            tesseract_cmd: Path to tesseract binary (optional)
            use_vision_fallback: Use Llama Vision if Tesseract fails
        """
        self.engine = engine
        self.use_vision_fallback = use_vision_fallback
        
        if tesseract_cmd and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        logger.info(f"OCR Engine initialized: {engine}")
    
    def process_document(
        self,
        source: Union[str, Path, bytes, Image.Image],
        dpi: int = 300
    ) -> OCRResult:
        """
        Process a document and extract text.
        
        Args:
            source: File path, bytes, or PIL Image
            dpi: DPI for PDF to image conversion
            
        Returns:
            OCRResult with extracted text and metadata
        """
        logger.info("Processing document for OCR")
        
        # Convert source to images
        images = self._load_images(source, dpi)
        
        if not images:
            raise ValueError("No images could be extracted from document")
        
        # Process each page
        blocks = []
        all_text = []
        
        for page_num, image in enumerate(images, start=1):
            try:
                if self.engine == "tesseract" or self.engine == "auto":
                    page_result = self._process_with_tesseract(image, page_num)
                else:
                    page_result = self._process_with_vision(image, page_num)
                
                blocks.extend(page_result["blocks"])
                all_text.append(page_result["text"])
                
            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                
                # Try fallback
                if self.use_vision_fallback and self.engine != "llama_vision":
                    logger.info("Attempting Llama Vision fallback")
                    try:
                        page_result = self._process_with_vision(image, page_num)
                        blocks.extend(page_result["blocks"])
                        all_text.append(page_result["text"])
                    except Exception as vision_error:
                        logger.error(f"Vision fallback failed: {vision_error}")
                        all_text.append(f"[Error processing page {page_num}]")
        
        full_text = "\n\n".join(all_text)
        
        return OCRResult(
            text=full_text,
            blocks=blocks,
            pages=len(images),
            engine=self.engine,
            metadata={
                "total_blocks": len(blocks),
                "avg_confidence": sum(b.confidence for b in blocks) / len(blocks) if blocks else 0.0
            }
        )
    
    def _load_images(
        self,
        source: Union[str, Path, bytes, Image.Image],
        dpi: int
    ) -> List[Image.Image]:
        """Load images from various source types"""
        
        # Already an image
        if isinstance(source, Image.Image):
            return [source]
        
        # Path to file
        if isinstance(source, (str, Path)):
            path = Path(source)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            # PDF file
            if path.suffix.lower() == '.pdf':
                logger.info(f"Converting PDF to images (DPI: {dpi})")
                return convert_from_path(str(path), dpi=dpi)
            
            # Image file
            else:
                return [Image.open(path)]
        
        # Bytes
        if isinstance(source, bytes):
            # Try as PDF first
            try:
                return convert_from_bytes(source, dpi=dpi)
            except:
                # Try as image
                return [Image.open(io.BytesIO(source))]
        
        raise ValueError(f"Unsupported source type: {type(source)}")
    
    def _process_with_tesseract(
        self,
        image: Image.Image,
        page_num: int
    ) -> dict:
        """Process image with Tesseract OCR"""
        
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract not available")
        
        logger.debug(f"Processing page {page_num} with Tesseract")
        
        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text
        text = pytesseract.image_to_string(image)
        
        # Build blocks
        blocks = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            if int(ocr_data['conf'][i]) > 0:  # Valid confidence
                block = DocumentBlock(
                    text=ocr_data['text'][i],
                    page=page_num,
                    confidence=float(ocr_data['conf'][i]) / 100.0,
                    bbox=(
                        ocr_data['left'][i],
                        ocr_data['top'][i],
                        ocr_data['left'][i] + ocr_data['width'][i],
                        ocr_data['top'][i] + ocr_data['height'][i]
                    ),
                    block_type="text"
                )
                blocks.append(block)
        
        return {
            "text": text,
            "blocks": blocks
        }
    
    def _process_with_vision(
        self,
        image: Image.Image,
        page_num: int
    ) -> dict:
        """
        Process image with Llama Vision via Ollama.
        
        Prompt asks for:
        - Text transcription
        - Layout structure hints
        - Table detection
        """
        
        logger.debug(f"Processing page {page_num} with Llama Vision")
        
        # Import here to avoid circular dependency
        from ..llm.ollama import OllamaClient
        
        client = OllamaClient()
        
        # Save image to temp buffer
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Vision prompt
        prompt = """Extract all text from this medical document image.
        
Provide:
1. Complete text transcription
2. Structure notes (tables, forms, sections)
3. Any handwritten text visible

Format as plain text, maintaining layout where possible."""
        
        response = client.vision_completion(
            prompt=prompt,
            image_data=buffer.getvalue()
        )
        
        # Parse response
        text = response.get("text", "")
        
        # Create single block (vision doesn't give bbox data)
        block = DocumentBlock(
            text=text,
            page=page_num,
            confidence=0.85,  # Assumed confidence for vision
            bbox=None,
            block_type="text"
        )
        
        return {
            "text": text,
            "blocks": [block]
        }


def extract_text_from_file(file_path: Union[str, Path]) -> str:
    """
    Convenience function to extract text from a file.
    
    Args:
        file_path: Path to document file
        
    Returns:
        Extracted text
    """
    engine = OCREngine(engine="auto")
    result = engine.process_document(file_path)
    return result.text
