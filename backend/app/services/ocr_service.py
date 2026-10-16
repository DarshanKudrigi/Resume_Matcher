import io
import logging
from typing import Tuple, Optional

logger = logging.getLogger("resumemate.ocr")

def is_ocr_available() -> bool:
    """Checks whether pytesseract and pdf2image are installed and usable."""
    try:
        import pytesseract
        import pdf2image
        # Check if tesseract binary can be queried
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    except ImportError:
        return False

def extract_text_via_ocr(pdf_bytes: bytes) -> Tuple[str, bool, Optional[str]]:
    """
    Attempts to extract text from a scanned PDF by rendering pages to images
    and applying Tesseract OCR.
    
    Returns:
        Tuple of (extracted_text, success_flag, status_message)
    """
    try:
        import pytesseract
        import pdf2image
    except ImportError:
        msg = "OCR libraries (pytesseract, pdf2image) are not installed. Digital PDF text was insufficient."
        logger.info(msg)
        return "", False, msg

    try:
        images = pdf2image.convert_from_bytes(pdf_bytes, dpi=200, fmt="png")
        if not images:
            return "", False, "No renderable pages found in PDF for OCR."
        
        extracted_pages = []
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img)
            if page_text and page_text.strip():
                extracted_pages.append(page_text.strip())
        
        full_text = "\n\n".join(extracted_pages)
        if full_text.strip():
            logger.info(f"OCR successfully extracted {len(full_text.split())} words across {len(images)} page(s).")
            return full_text, True, "OCR extraction successful."
        else:
            return "", False, "OCR scanned document but could not identify readable text."
            
    except Exception as e:
        err_msg = f"OCR processing failed: {str(e)}"
        logger.warning(err_msg)
        return "", False, err_msg
