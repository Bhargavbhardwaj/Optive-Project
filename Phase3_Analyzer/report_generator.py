import csv
from tabulate import tabulate

def generate_report(results, output_csv="phase3_report.csv", output_txt="phase3_report.txt"):
    # results - list of tuples/lists, each row = one file’s analysis.
    headers = ["File Name", "File Type", "File Description", "Key Findings"]

    # save csv
    with open(output_csv,"w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)  # writing headers - column names
        writer.writerows(results) # write all rows from results


    table = tabulate(results, headers=headers, tablefmt = "grid")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(table)

    print("\n[REPORT GENERATED") # print the same formatted table in the console for immediate viewing.
    print(table)