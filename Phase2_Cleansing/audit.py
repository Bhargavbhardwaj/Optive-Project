'''This audit.py module is responsible for keeping track
of what happened during PII detection & masking — i.e.,
a structured audit log in a CSV file.'''

import csv
import datetime
from tabulate import tabulate
import pandas as pd

"""
This audit.py module is responsible for keeping track
of what happened during PII detection & masking — i.e.,
a structured audit log in multiple formats (CSV, TXT, Excel).
"""

import csv
import datetime
from tabulate import tabulate
import pandas as pd


class AuditLogger:
    def __init__(self, csv_path="audit_log.csv"):
        self.csv_path = csv_path
        self.rows = []
        self.headers = [
            "timestamp", "input_file", "output_file",
            "detector", "detection_type", "original_snippet",
            "action", "notes"
        ]

    def write_row(self, input_file, output_file, detector,
                  detection_type, original_snippet, action, notes=""):
        row = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "input_file": input_file,
            "output_file": output_file,
            "detector": detector,
            "detection_type": detection_type,
            "original_snippet": str(original_snippet).replace("\n", " ")[:200],
            "action": action,
            "notes": notes
        }
        self.rows.append(row)

    def save(self):
        # Save to CSV
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.rows)

        # Save to TXT (tabular view)
        table = tabulate(self.rows, headers="keys", tablefmt="grid")
        with open("audit_log.txt", "w", encoding="utf-8") as f:
            f.write(table)

        # Save to Excel (consultant-friendly)
        df = pd.DataFrame(self.rows)
        df.to_excel("audit_log.xlsx", index=False)

        print(f"[DONE] Audit logs saved → {self.csv_path}, audit_log.txt, audit_log.xlsx")


# def init_audit(csv_path = "audit_log.csv"): # initializing the audit logging
#
#     f = open(csv_path, "w",newline="", encoding="utf-8")
#     writer = csv.writer(f)  # creating a csv writer object
#     writer.writerow(["timestamp","input_file","output_file","detector","detection_type",
#                      "original_snippet", "action", "notes"])
#     return f, writer
#
# def write_audit_row(writer, input_file, output_file, detector, detection_type, original_snippet,
#                     action, notes=""):  # writes a new row in the audit log with the provided details
#     writer.writerow([
#         datetime.datetime.utcnow().isoformat(), # exact time
#         input_file,
#         output_file,
#         detector, detection_type, # detection engine and detected item
#         str(original_snippet).replace("\n", " ")[:200], # makes sure that multiple snippets don't break csv formatting
#         action,  # what action was taken
#         notes # to add any extra info
#     ])