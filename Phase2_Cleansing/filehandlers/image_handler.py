'''This function takes an image, runs OCR to detect text + bounding boxes,
checks each word for PII, and then masks (black box) or removes (white box)
the sensitive text directly from the image. It also writes an audit log entry
for every detection and finally saves the sanitized image.'''

from ..detectors import detect_pii_in_text
#from ..audit import write_audit_row
#from Phase2_Cleansing.audit import AuditLogger
#audit = AuditLogger("audit_log.csv")


try:
    import pytesseract  # Python wrapper for Tesseract OCR (extracts text from images).
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    from PIL import Image # opens/handles images in Python. PIL= Pillow
    import cv2  # edits/draws on images (used here to black out/white out boxes).
    HAS_LIBS = True
except Exception as e:
    print(f"[WARN] Required libraries for image handling are missing: {e}")
    HAS_LIBS = False

def clean_image_file(input_path, output_path, action, use_spacy, audit):
    if not HAS_LIBS:
        print(f"[FAIL] Missing OCR/image libraries for {input_path}")
        return False
    try:
        img_cv = cv2.imread(input_path)  # loads the image in OpenCV format (NumPy array) → used for editing.
        if img_cv is None:
            print(f"[FAIL] Could not read image file: {input_path}")
            return False

        try:
            pil_img = Image.open(input_path).convert("RGB")  # loads the same image in Pillow format (RGB) → used for OCR.
        except Exception as e:
            print(f"[FAIL] PIL cannot open {input_path}: {e}")
            return False

        # OCR (extract text with bounding boxes)
        #Runs Tesseract OCR on the image.
        #Returns a dictionary with info for each detected word, including:
               #text → the recognized text
               #left, top, width, height → bounding box coordinates
               #level → hierarchy of OCR (page, block, paragraph, line, word).
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
        n_boxes = len(data['level'])
        for i in range(n_boxes): # Loops through every detected word (n_boxes).
            txt = data['text'][i].strip() # txt is the actual word recognized.
            if not txt: # Skip empty words (OCR sometimes returns blanks).
                continue
            detections = detect_pii_in_text(txt, use_spacy=use_spacy)

            # Mask or remove detected text
            if detections:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                if action == "mask":  # If action = "mask" → draw a black rectangle over it
                    cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 0, 0), thickness=-1)
                elif action == "remove": # If action = "remove" → draw a white rectangle over it.
                    cv2.rectangle(img_cv, (x, y), (x + w, y + h), (255, 255, 255), thickness=-1)  # thickness=-1 → fills the rectangle completely

                # logs the action
                for d in detections:
                    audit.write_row(input_path, output_path,
                                    d.get("source"), d.get("type"), d.get("match"),
                                    action, notes=f"box:{i}")

# save the cleaned image
        cv2.imwrite(output_path, img_cv)  # Writes the modified OpenCV image (img_cv) to output_path.
        return True
    except pytesseract.TesseractNotFoundError:
        print(f"[FAIL] Tesseract OCR not installed or not in PATH for {input_path}")
        return False
    except Exception as e:
        print(f"[FAIL] Error processing {input_path}: {e}")
        return False

