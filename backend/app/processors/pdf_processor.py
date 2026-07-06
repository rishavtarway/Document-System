from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


class PDFProcessor:
    @staticmethod
    def extract_text(file_path: Path) -> str:
        try:
            doc = fitz.open(str(file_path))
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text.strip()
        except Exception:
            return ""
    
    @staticmethod
    def extract_images(file_path: Path) -> list[bytes]:
        images = []
        try:
            doc = fitz.open(str(file_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img in page.get_images():
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    images.append(base_image["image"])
            doc.close()
        except Exception:
            pass
        return images
    
    @staticmethod
    def get_page_count(file_path: Path) -> int:
        try:
            doc = fitz.open(str(file_path))
            count = len(doc)
            doc.close()
            return count
        except Exception:
            return 0
