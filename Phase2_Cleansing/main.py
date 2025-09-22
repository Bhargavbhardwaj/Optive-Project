import os
import argparse  # to handle command_line arguments
import csv  # to read phase 1 metadata CSVs

from .utils import ensure_dir  # makes sure an output directory exists
from .audit import AuditLogger  # initialize audit_log.csv

# cleansing functions for each file type
from .filehandlers.text_handler import clean_text_file
from .filehandlers.pdf_handler import clean_pdf_file
from .filehandlers.excel_handler import clean_xlsx_file
from .filehandlers.pptx_handler import clean_pptx_file
from .filehandlers.doc_handler import clean_doc_file
from .filehandlers.image_handler import clean_image_file

audit = AuditLogger("audit_log.csv")


# def normalize_type(file_type, filename):
#     """
#     Normalize MIME types or extensions into simple extensions (pdf, png, etc.).
#     """
#     if "/" in file_type:  # MIME type
#         if "pdf" in file_type: return "pdf"
#         if "word" in file_type or "doc" in file_type: return "docx"
#         if "presentation" in file_type or "ppt" in file_type: return "pptx"
#         if "spreadsheet" in file_type or "excel" in file_type: return "xlsx"
#         if "image" in file_type:
#             return os.path.splitext(filename)[-1].lower().strip(".")
#         return os.path.splitext(filename)[-1].lower().strip(".")
#
#     return file_type.lower().strip(".")
def normalize_type(file_type, filename):
    ext = os.path.splitext(filename)[-1].lower().strip(".")  # get extension

    if "/" in file_type:  # MIME type
        if "pdf" in file_type: return "pdf"
        if "word" in file_type or file_type.startswith("application/vnd.openxmlformats-officedocument.wordprocessingml"):
            return "docx"
        if "presentation" in file_type or file_type.startswith("application/vnd.openxmlformats-officedocument.presentationml"):
            return "pptx"
        if "spreadsheet" in file_type or file_type.startswith("application/vnd.openxmlformats-officedocument.spreadsheetml"):
            return "xlsx"
        if "image" in file_type:
            return ext
    return ext


def route_file(input_path, output_path, file_type, action, use_spacy, audit):


    # Routes file to appropriate handler based on type - similar to a dispatcher
    try:

       file_type = file_type.lower()  # Normalize file extension like  PDF → pdf

# If extension matches ,  send file to the right handler.
       if file_type in ["txt", "csv", "log", "json"]:
           return clean_text_file(input_path, output_path, action, use_spacy, audit)

       elif file_type == "pdf":
           return clean_pdf_file(input_path, output_path, action, use_spacy, audit)

       elif file_type in ["xlsx", "xls"]:
           return clean_xlsx_file(input_path, output_path, action, use_spacy, audit)

       elif file_type == "pptx":
           return clean_pptx_file(input_path, output_path, action, use_spacy, audit)

       elif file_type == "docx":
           return clean_doc_file(input_path, output_path, action, use_spacy, audit)

       elif file_type in ["png", "jpg", "jpeg"]:
           return clean_image_file(input_path, output_path, action, use_spacy, audit)

       else:
           print(f"[WARN] Unsupported file type: {file_type} ({input_path})")
           return False
    except Exception as  e:
        print(f"[FAIL] {input_path} → {file_type}: {e}")
        return False


def main():

    # entry point to run the script
    parser = argparse.ArgumentParser(description="Phase 2: File Cleansing and Analysis")

    # must provide a file/folder containing files or a phase 1 CSV files with metadata
    parser.add_argument("--input", "-i", required=True,
                        help="Path to a file, folder, or CSV metadata file from Phase 1")
    # --output (or -o) - where to save cleansed files (default: cleansed_output/).
    parser.add_argument("--output", "-o", default="cleansed_output",
                        help="Output directory for cleansed files")

    #--action - what to do with PII:
    parser.add_argument("--action", "-a", choices=["mask", "remove"], default="mask",
                        help="Whether to mask or remove PII")

    # --use-spacy - flag to enable spaCy NER in addition to regex rules
    parser.add_argument("--use-spacy", action="store_true",
                        help="Enable spaCy NER in addition to regex detection")

    args = parser.parse_args()  # Parses the arguments from the command line

    # Prepare output directory and audit log
    ensure_dir(args.output) # Creates output directory if it doesn’t exist.
    audit = AuditLogger("audit_log.csv")  # initializes the log file

    # Case 1: CSV metadata input (from Phase 1)
    if args.input.endswith(".csv"):
        with open(args.input, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                input_file = row.get("Full Path", row["Filename"])
                file_type = normalize_type(row["File Type"], row["Filename"])  # e.g. application/pdf → pdf
                output_file = os.path.join(args.output, os.path.basename(input_file))

                success = route_file(input_file, output_file, file_type, args.action,
                                     args.use_spacy, audit)

                if success:
                    print(f"[OK] Cleansed {input_file} → {output_file}")
                else:
                    print(f"[FAIL] Could not cleanse {input_file}")

    # Case 2: Folder input
    elif os.path.isdir(args.input):
        for root, _, files in os.walk(args.input):
            for file in files:
                input_file = os.path.join(root, file)
                ext = os.path.splitext(file)[-1].lower().strip(".")
                output_file = os.path.join(args.output, file)

                success = route_file(input_file, output_file, ext, args.action,
                                     args.use_spacy, audit)

                if success:
                    print(f"[OK] Cleansed {input_file} → {output_file}")
                else:
                    print(f"[FAIL] Could not cleanse {input_file}")

    # Case 3: Single file input
    else:
        file = os.path.basename(args.input)
        ext = os.path.splitext(file)[-1].lower().strip(".")
        output_file = os.path.join(args.output, file)

        success = route_file(args.input, output_file, ext, args.action,
                             args.use_spacy, audit)

        if success:
            print(f"[OK] Cleansed {args.input} → {output_file}")
        else:
            print(f"[FAIL] Could not cleanse {args.input}")

    audit.save()
    print("[DONE] Audit log written to audit_log.csv")


if __name__ == "__main__":
    main()
