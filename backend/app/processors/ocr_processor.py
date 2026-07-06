from __future__ import annotations

from pathlib import Path
from typing import Optional


class OCRProcessor:
    @staticmethod
    async def process(file_path: Path) -> str:
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            return await OCRProcessor._ocr_pdf(file_path)
        elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".tif"):
            return await OCRProcessor._ocr_image(file_path)
        elif ext == ".txt":
            return await OCRProcessor._read_text(file_path)
        else:
            return ""
    
    @staticmethod
    async def _ocr_pdf(file_path: Path) -> str:
        from app.processors.pdf_processor import PDFProcessor
        text = PDFProcessor.extract_text(file_path)
        
        if text and len(text.strip()) > 50:
            return text
        
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(str(file_path), dpi=300)
            ocr_text = []
            for img in images:
                t = pytesseract.image_to_string(img)
                ocr_text.append(t)
            return "\n".join(ocr_text)
        except Exception:
            return text
    
    @staticmethod
    async def _ocr_image(file_path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image
            image = Image.open(str(file_path))
            return pytesseract.image_to_string(image)
        except Exception:
            return ""
    
    @staticmethod
    async def _read_text(file_path: Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""
