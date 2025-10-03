import os
import argparse # to make the script run from command line with arguments
import csv

from .extractors import extract_content
from .interpreters import interpret_content
from .report_generator import generate_report

def normalize_ext(file_type, filename):
    """
    Normalize MIME types or raw extensions into a clean extension (pdf, xlsx, pptx, etc.)
    """
    ext = os.path.splitext(filename)[-1].lower().strip(".")  # fallback: file extension

    if "/" in file_type:  # MIME type
        if "pdf" in file_type:
            return "pdf"
        if "word" in file_type or file_type.startswith("application/vnd.openxmlformats-officedocument.wordprocessingml"):
            return "docx"
        if "presentation" in file_type or "ppt" in file_type:
            return "pptx"
        if "spreadsheet" in file_type or "excel" in file_type:
            return "xlsx"
        if "image" in file_type:
            return ext

    return ext or file_type

# def main():
#     parser = argparse.ArgumentParser(description="Phase 3: File Analysis & Report Generation")
#     parser.add_argument("--input", "-i", required=True,
#                         help="Path to cleansed_output folder or Phase1 metadata CSV")
#     parser.add_argument("--output", "-o", default="phase3_output",
#                         help="Output folder for reports")
#     args = parser.parse_args()  # parses the actual user input.
#
#     os.makedirs(args.output, exist_ok=True) # creates the output folder if it doesn’t exist.
#
#     results = []  # empty list  to collect findings for each file
#
#     #  CSV input from Phase 1 like metadata.csv
#     if args.input.endswith(".csv"):
#         with open(args.input, newline="", encoding="utf-8") as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 try:
#                     file_path = row.get("Full Path", row["Filename"])
#                     file_type = normalize_ext(row["File Type"], row["Filename"])
#
#                     text = extract_content(file_path, file_type) # gets text from file
#                     desc, findings = interpret_content(text, file_type)
#
#                     results.append([os.path.basename(file_path), f".{file_type}", desc, findings])
#                 except Exception as e:
#                     print(f"[WARN] Skipping {row.get('Filename')} → {e}")
#                 # file_path = row.get("Full Path", row["Filename"])
#                 # file_type = row["File Type"].split("/")[-1]
#                 # text = extract_content(file_path, file_type) # gets text from file
#                 # desc, findings = interpret_content(text, file_type)
#                 # results.append([os.path.basename(file_path), f".{file_type}", desc, findings])  # append the findings
#
#
#     # Case 2: Folder input
#     elif os.path.isdir(args.input):
#         for root, _, files in os.walk(args.input):
#             for file in files:
#                 try:
#                     file_path = os.path.join(root, file)
#                     ext = os.path.splitext(file)[-1].lower().strip(".")
#
#                     text = extract_content(file_path, ext)
#                     desc, findings = interpret_content(text, ext)
#
#                     results.append([file, f".{ext}", desc, findings])
#                 except Exception as e:
#                     print(f"[WARN] Skipping {file} → {e}")
#
#     else:
#         print(f"[ERROR] Input path not found: {args.input}")
#         return
#
#
#     output_csv = os.path.join(args.output, "phase3_report.csv") # machine readdable report
#     output_txt = os.path.join(args.output, "phase3_report.txt") # human- readable report
#
#     generate_report(results, output_csv, output_txt)
#
#     print(f"[DONE] Phase 3 report saved → {args.output}")
#
# if __name__ == "__main__":
#     main()


def run_phase3(input_path, output_dir="phase3_output"):
    """
    Run Phase 3: Analyze cleansed files and generate reports.
    Accepts:
      - CSV metadata (Phase 1 output)
      - Folder of cleansed files
    Returns:
      Dict with results, CSV path, TXT path.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    # Case 1: CSV input
    if input_path.endswith(".csv"):
        with open(input_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    file_path = row.get("Full Path", row["Filename"])
                    file_type = normalize_ext(row["File Type"], row["Filename"])
                    text = extract_content(file_path, file_type)
                    desc, findings = interpret_content(text, file_type)
                    results.append([os.path.basename(file_path), f".{file_type}", desc, findings])
                except Exception as e:
                    print(f"[WARN] Skipping {row.get('Filename')} → {e}")

    # Case 2: Folder input
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[-1].lower().strip(".")
                    text = extract_content(file_path, ext)
                    desc, findings = interpret_content(text, ext)
                    results.append([file, f".{ext}", desc, findings])
                except Exception as e:
                    print(f"[WARN] Skipping {file} → {e}")

    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")

    # Generate reports
    output_csv = os.path.join(output_dir, "phase3_report.csv")
    output_txt = os.path.join(output_dir, "phase3_report.txt")
    generate_report(results, output_csv, output_txt)

    return {
        # "results": results,
        # "csv_path": output_csv,
        # "txt_path": output_txt,
        "results": results,
        "csv_path": output_csv,
        "txt_path": output_txt,
        "output_dir": output_dir
    }


# CLI compatibility
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 3: File Analysis & Report Generation")
    parser.add_argument("--input", "-i", required=True,
                        help="Path to cleansed_output folder or Phase1 metadata CSV")
    parser.add_argument("--output", "-o", default="phase3_output",
                        help="Output folder for reports")
    args = parser.parse_args()

    result = run_phase3(args.input, args.output)
    print(f"[DONE] Phase 3 report saved → {args.output}")
    print("CSV:", result["csv_path"])
    print("TXT:", result["txt_path"])


