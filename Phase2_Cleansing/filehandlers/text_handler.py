''' The function takes a text file, finds PII inside it, cleans it (mask/remove), writes the cleaned version to a new file,
 and logs every detection in an audit log.
'''

from ..detectors import detect_pii_in_text
from ..maskers import mask_text
#from ..audit import write_audit_row
from Phase2_Cleansing.audit import AuditLogger
audit = AuditLogger("audit_log.csv")



def clean_text_file(input_path, output_path, action, use_spacy, audit):
    try:
        with open(input_path, "r",encoding="utf-8", errors="ignore") as f: ## skips invalid character instead of crashing
            text = f.read()
    except Exception: # returns false, if file doesn't exist
        return False

# detects sensitive information
    detections = detect_pii_in_text(text, use_spacy=use_spacy)

# texts are passed into mask_text and action is taken and cleaned result is stored in cleaned_text
    cleaned_text = mask_text(text, detections, action=action)

    with open(output_path, "w", encoding="utf-8") as f: # opens in write mode
        f.write(cleaned_text) # and writes the sanitized text in it

    for d in detections:  # loops through every detection found
        audit.write_row(   # calls to log it
            input_file=input_path,
            output_file=output_path,
            detector=d.get("source"),
            detection_type=d.get("type"),
            original_snippet=d.get("match"),  # the actual matched string
            action=action
        )
    return True


