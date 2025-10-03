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
        return [os.path.basename(file_path), f"Error: {str(e)}"]

# function to handle input
def process_input(input_path, results = None):

    if results is None:

        results = []
    if zipfile.is_zipfile(input_path):
        with zipfile.ZipFile(input_path, 'r') as z:
            extract_dir = "extracts_files"  # if input is a ZIP file, then everything is extracted into a folder called "Extracted_files"
            os.makedirs(extract_dir, exist_ok=True)
            z.extractall(extract_dir)
            for name in z.namelist(): # loops each file and processes it with process_file()
                file_path = os.path.join(extract_dir, name)
                if os.path.isfile(file_path):
                    results.append(process_file(file_path))

    else:
        results.append(process_file(input_path))
    return results # returns a list of all file metadata


# if __name__ == "__main__":
#     input_path = "../Analysis Files.zip"  # give the file name of path here
#     files_metadata = process_input(input_path)
#
#     headers = ["Filename","Full Path", "File Type"]
#     table = tabulate(files_metadata, headers=headers, tablefmt="grid")
#     print(table)
#
# # save to text file
#     with open("files_metadata.txt", "w", encoding="utf-8") as f:
#         f.write(table)
#
# # save to CSV file
#     with open("files_metadata.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(headers)
#         writer.writerows(files_metadata)
#
# # total file count and types
#     file_types = [row[2] for row in files_metadata]
#     counts = Counter(file_types)
#
#     print("\nFile Type Summary: ")
#     for ftype, count in counts.items():
#         print(f"{ftype}: {count}")
#
#     print("\nMatadata saved to file_metadata.txt and file_metadata.csv")
#


def run_phase1(input_path, output_dir="phase1_output"):
    """
    Run Phase 1: Analyze files/ZIP and extract metadata.
    Returns dict with results, csv_path, txt_path.
    """
    os.makedirs(output_dir, exist_ok=True)

    files_metadata = process_input(input_path)

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

    # File type summary
    file_types = [row[2] for row in files_metadata]
    counts = Counter(file_types)

    return {
        # "results": files_metadata,
        # "csv_path": csv_path,
        # "txt_path": txt_path,
        # "counts": counts,
        "results": files_metadata,
        "csv_path": os.path.join(output_dir, "files_metadata.csv"),
        "txt_path": os.path.join(output_dir, "files_metadata.txt")
    }


# CLI compatibility
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 1: File Analyzer")
    #parser.add_argument("--input", "-i", required=True, help="Path to file or ZIP archive")
    parser.add_argument("--input", "-i",default="Analysis Files.zip", help="Path to file or ZIP archive (default: 'Analysis Files.zip')")

    parser.add_argument("--output", "-o", default="phase1_output", help="Output folder")
    args = parser.parse_args()

    result = run_phase1(args.input, args.output)
    print(f"[DONE] Phase 1 → Metadata saved in {args.output}")
    print("CSV:", result["csv_path"])
    print("TXT:", result["txt_path"])