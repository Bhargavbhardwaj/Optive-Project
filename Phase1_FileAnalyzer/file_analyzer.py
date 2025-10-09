import os # helps work with files and folders like getting file paths and all.
import zipfile  # helps open/extract zipfiles
import magic  # helps detect file type by looking at file contents and not just extensions
import mimetypes  # backup methods to guess file type using the file extension
from tabulate import tabulate # helps result look like  a clean table
import csv
from collections import Counter

''' This code takes  a ZIP file or a single file as input. Extracts files (if ZIP). Detects what type of file each one is.
Shows results in a nice table format (only Filename + File Type) and saves that table into a .txt file. '''



def detect_file_type(file_path): # detecting file types using python-magic, fallback to mimetypes
    try:
        mime = magic.from_file(file_path, mime = True) # first file is detected by magic moudule which is very accurate
    except Exception:
        mime = None
    if not mime: # if magic fails, then mimetypes is tried and returns unknown if both fails
        mime,_ = mimetypes.guess_type(file_path)
    return mime or "Unknown"

# function to process single file

def process_file(file_path): # return only filename and file type
    try:
        return [os.path.basename(file_path), os.path.abspath(file_path),
                detect_file_type(file_path)]  # gets just the filename from full path
    except Exception as e:
        return [os.path.basename(file_path), f"Error: {str(e)}", "Unknown"]

# function to handle input
# def process_input(input_path,output_dir, results = None):
#
#     if results is None:
#
#         results = []
#     if zipfile.is_zipfile(input_path):
#         extract_dir =os.path.join(output_dir, "extracted_files")  #   if input is a ZIP file, then everything is extracted into a folder called "Extracted_files"
#
#         os.makedirs(extract_dir, exist_ok=True)
#
#
#
#         with zipfile.ZipFile(input_path, 'r') as z:
#             z.extractall(extract_dir)
#             for name in z.namelist():
#                 file_path = os.path.join(extract_dir, name)
#                 if os.path.isfile(file_path):
#                     # Recursively handle nested zips or subfolders
#                     process_input(file_path, output_dir, results)
#
#     elif os.path.isdir(input_path):
#         for root, _, files in os.walk(input_path):
#             for file in files:
#                 process_input(os.path.join(root, file), output_dir, results)
#
#
#
#     else:
#         results.append(process_file(input_path))
#     return results # returns a list of all file metadata
def process_input(input_path, output_dir, results=None):
    """Recursively process files, directories, and ZIP archives."""
    if results is None:
        results = []

    if zipfile.is_zipfile(input_path):
        extract_dir = os.path.join(output_dir, "extracted_files", os.path.splitext(os.path.basename(input_path))[0])
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(input_path, 'r') as z:
            z.extractall(extract_dir)

        # After extraction, walk through everything extracted
        for root, _, files in os.walk(extract_dir):
            for file in files:
                process_input(os.path.join(root, file), output_dir, results)

    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                process_input(os.path.join(root, file), output_dir, results)

    elif os.path.isfile(input_path):
        results.append(process_file(input_path))

    return results





def run_phase1(input_path, output_dir="phase1_output"):
    """
    Run Phase 1: Analyze files/ZIP and extract metadata.
    Saves table to CSV and TXT, returns metadata info.
    """
    os.makedirs(output_dir, exist_ok=True)

    files_metadata = process_input(input_path, output_dir)

    headers = ["Filename", "Full Path", "File Type"]
    table = tabulate(files_metadata, headers=headers, tablefmt="grid")

    # Save TXT
    txt_path = os.path.join(output_dir, "files_metadata.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(table)

    # Save CSV
    csv_path = os.path.join(output_dir, "files_metadata.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(files_metadata)

    # Print summary
    file_types = [row[2] for row in files_metadata]
    counts = Counter(file_types)

    print("\n📊 File Type Summary:")
    for ftype, count in counts.items():
        print(f"{ftype}: {count}")

    print(f"\n✅ Metadata saved to:\n  {txt_path}\n  {csv_path}")

    return {
        "results": files_metadata,
        "csv_path": csv_path,
        "txt_path": txt_path
    }



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 1: File Analyzer")
    parser.add_argument("--input", "-i", required=True, help="Path to file or ZIP archive")
    parser.add_argument("--output", "-o", default="phase1_output",
                        help="Output folder for metadata and extracted files")
    args = parser.parse_args()

    result = run_phase1(args.input, args.output)

    # Print table on terminal
    headers = ["Filename", "Full Path", "File Type"]
    print("\n" + tabulate(result["results"], headers=headers, tablefmt="grid"))

    print(f"\n[DONE] Phase 1 complete → CSV: {result['csv_path']}")