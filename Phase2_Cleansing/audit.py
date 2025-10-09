'''This audit.py module is responsible for keeping track
of what happened during PII detection & masking — i.e.,
a structured audit log in a CSV file.'''



import os
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
        base_dir = os.path.dirname(self.csv_path) or "."
        txt_path = os.path.join(base_dir, "audit_log.txt")
        xlsx_path = os.path.join(base_dir, "audit_log.xlsx")

        # Save to CSV
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.rows)

        # Save to TXT
        table = tabulate(self.rows, headers="keys", tablefmt="grid")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(table)

        # Save to Excel
        df = pd.DataFrame(self.rows)
        df.to_excel(xlsx_path, index=False)

        print(f"[DONE] Audit logs saved → {self.csv_path}, {txt_path}, {xlsx_path}")
