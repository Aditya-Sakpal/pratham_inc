"""
OCR service for extracting text from uploaded images
Supports multiple OCR providers (Tesseract, EasyOCR, PaddleOCR, OpenAI Vision)
"""
import os
import base64
from typing import Optional
from PIL import Image
import io
from app.config import settings


class OCRService:
    """Service for OCR text extraction from images"""
    
    def __init__(self):
        """Initialize OCR service based on configuration"""
        self.provider = settings.OCR_PROVIDER.lower()
        self._init_provider()
    
    def _init_provider(self):
        """Initialize the selected OCR provider"""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                raise ImportError("openai not installed. Install with: pip install openai")
        elif self.provider == "tesseract":
            try:
                import pytesseract
                self.ocr_engine = pytesseract
            except ImportError:
                raise ImportError("pytesseract not installed. Install with: pip install pytesseract")
        elif self.provider == "easyocr":
            try:
                import easyocr
                self.reader = easyocr.Reader(['en'])
            except ImportError:
                raise ImportError("easyocr not installed. Install with: pip install easyocr")
        elif self.provider == "paddleocr":
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            except ImportError:
                raise ImportError("paddleocr not installed. Install with: pip install paddleocr")
        else:
            raise ValueError(f"Unsupported OCR provider: {self.provider}")
    
    def extract_text(self, image_data: bytes) -> dict:
        """
        Extract text from image
        
        Args:
            image_data: Image file bytes
            
        Returns:
            Dictionary with extracted text and confidence
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            if self.provider == "openai":
                # Encode image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                # Call OpenAI Vision API
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # or "gpt-4o" for better accuracy
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Extract all text from this image. If it contains handwritten quiz answers, extract each answer on a new line. Only output the text, no explanations."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                
                extracted_text = response.choices[0].message.content.strip()
                
                return {
                    "extracted_text": extracted_text,
                    "confidence": 0.95  # OpenAI Vision is highly accurate
                }
            
            elif self.provider == "tesseract":
                text = self.ocr_engine.image_to_string(image)
                # Get confidence data
                data = self.ocr_engine.image_to_data(image, output_type=self.ocr_engine.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                return {
                    "extracted_text": text.strip(),
                    "confidence": avg_confidence / 100.0  # Normalize to 0-1
                }
            
            elif self.provider == "easyocr":
                results = self.reader.readtext(image)
                text_parts = [result[1] for result in results]
                confidences = [result[2] for result in results]
                
                return {
                    "extracted_text": "\n".join(text_parts),
                    "confidence": sum(confidences) / len(confidences) if confidences else 0.0
                }
            
            elif self.provider == "paddleocr":
                results = self.ocr.ocr(image, cls=True)
                text_parts = []
                for line in results[0] if results else []:
                    text_parts.append(line[1][0])
                
                return {
                    "extracted_text": "\n".join(text_parts),
                    "confidence": 0.85  # PaddleOCR doesn't provide easy confidence access
                }
            
        except Exception as e:
            return {
                "extracted_text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def extract_text_from_file(self, file_path: str) -> dict:
        """
        Extract text from image file
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary with extracted text and confidence
        """
        with open(file_path, 'rb') as f:
            image_data = f.read()
        return self.extract_text(image_data)


# Global instance
ocr_service = OCRService()

