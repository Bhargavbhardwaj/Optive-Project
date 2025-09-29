# Helps classify files (access logs, visitor logs, policies)
# and extract security insights without heavy ML.
# Based on text keywords, it categorizes the file and summarizes findings.

# rule-based interpretation of extracted text
def interpret_content(text,file_type):
    if not text or text.startswith("[ERROR]"): # ff extraction failed like empty text/error, it returns a message
        return ("Could not extract content", "No findings available")

    file_type = file_type.lower()

    if "card" in text.lower() and "reader" in text.lower():
        return ("Access Card Reader",
                "Digital access control using ID cards; "
                "tracks entries with timestamps; dependent on card validity.")

    if "fingerprint" in text.lower() or "biometric" in text.lower():
        return ("Biometric Attendance/Access System",
                "Uses biometric authentication; prevents proxy access;"
                " provides reliable and tamper-proof logs.")

    if "visitor" in text.lower() or "logbook" in text.lower():
        return ("Visitors Logbook",
                "Manual entry system; prone to errors and falsification; lacks automated tracking.")

    if "policy" in text.lower() or "firewall" in text.lower() or "ids" in text.lower():
        return ("Security Policy/Config File",
                "Contains security rules (IAM/Firewall/IDS); requires validation for misconfigurations.")

    # Default - If none of the above rules matched then treat it as generic file.
    snippet = text[:100].replace("\n", " ") # return first 100 characters as a preview
    return (f"Generic {file_type.upper()} File",
            f"Extracted snippet: {snippet}...")