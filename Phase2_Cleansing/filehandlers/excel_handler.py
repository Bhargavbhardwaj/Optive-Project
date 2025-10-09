'''this file opens an Excel file, scans every string cell for PII, masks or removes it, updates the file,
and logs what was found (including sheet name and cell location).'''


from ..detectors import detect_pii_in_text
from ..maskers import mask_text
from Phase2_Cleansing.audit import AuditLogger
#audit = AuditLogger("audit_log.csv")
#from ..audit import write_audit_row

try:
    import openpyxl  # library to play with excel (.xlsx) files
    HAS_OPENPYXL = True
except Exception as e:
    print(f"[WARN] openpyxl library missing: {e}")
    HAS_OPENPYXL = False

def clean_xlsx_file(input_path, output_path, action, use_spacy, audit):
    # output_path is new excel file where cleaned content will be saved.

    if not HAS_OPENPYXL:
        print(f"[FAIL] openpyxl library not installed, cannot process {input_path}")
        return False  # functions stops immediately if openpyxl is missing
    try:
        wb = openpyxl.load_workbook(input_path)  # loads the workbook from the excel file
    except FileNotFoundError:
        print(f"[FAIL] Excel file not found: {input_path}")
        return False
    except Exception as e:
        print(f"[FAIL] Could not open Excel file {input_path}: {e}")
        return False

    try:
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=False): # values_only=False ensures that we get the cell objects to update not just the cell values
                for cell in row:
                    if cell.value and isinstance(cell.value, str):  # only processes if call.value is a string, others aren't PIIs
                        detections = detect_pii_in_text(cell.value, use_spacy=use_spacy)  # start detction
                        if detections:  # if found, then pass it through mask_text
                            cleaned_value = mask_text(cell.value, detections, action=action)
                            cell.value = cleaned_value  # update the excel with cleaned value

                            for d in detections:  # now log the changes into audit log entry
                                audit.write_row(input_path, output_path, d.get("source"),
                                                d.get("type"), d.get("match"), action, notes=f"sheet:{sheet.title};cell:{cell.coordinate}")
  # notes shows the cell coordinates
        wb.save(output_path)
        return True
    except Exception as e:
        print(f"[FAIL] Error processing Excel file {input_path}: {e}")
        return False

