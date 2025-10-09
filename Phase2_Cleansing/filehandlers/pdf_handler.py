'''This code opens a PDF, scans its text for sensitive data,
finds where that data appears on the page, and either masks (black boxes)
 or removes (white boxes) it. It then logs what was found and saves a sanitized version of the file.'''

from ..detectors import detect_pii_in_text
# from ..maskers import mask_text
#from ..audit import write_audit_row
from Phase2_Cleansing.audit import AuditLogger
#audit = AuditLogger("audit_log.csv")

try:
    import fitz  # PyMuPDF - parent library
    HAS_PYMUPDF=True
except Exception:
    HAS_PYMUPDF = False

try:
    import pytesseract  # Tries to import Tesseract OCR + Pillow for extracting text from scanned PDFs/images
    from PIL import Image
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False

def clean_pdf_file(input_path, output_path, action, use_spacy, audit):
    if not HAS_PYMUPDF:
        return False
    try:
        doc = fitz.open(input_path)  # loads the PDF into memory
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")  # extracts visible texts from image
            detections = detect_pii_in_text(text, use_spacy=use_spacy)
            for d in detections: # For each detection:
                token = d["match"] # Extract the actual matched text (d["match"]).
                rects = page.search_for(token) or []  # Use page.search_for(token) → finds all rectangles (rects) where this text occurs on the page.
                for r in rects: # For each rectangle containing the sensitive text:
                    if action == "mask":
                        # following are redaction annotations, which will permanently hide the text once applied
                        page.add_redact_annot(r, fill=(0,0,0)) # overlay a black box (fill=(0,0,0)).
                    elif action == "remove":
                        page.add_redact_annot(r, fill=(1,1,1)) # overlay a white box (fill=(1,1,1)).
                audit.write_row(input_path, output_path,
                                d.get("source"), d.get("type"), d.get("match"),action,
                                notes=f"page{page_num+1}")

        doc.save(output_path, garbage=4, deflate=True)
        # garbage=4 → removes unused objects from the PDF (cleanup).
        # deflate=True → compresses streams (reduces size).
        doc.close()
        return True
    except Exception:
        return False



