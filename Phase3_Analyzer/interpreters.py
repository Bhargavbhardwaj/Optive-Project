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
                "Tracks physical entry via ID cards with timestamps. Useful for monitoring movement, "
                "but vulnerable to lost/stolen cards and tailgating risks.")

    if "fingerprint" in text.lower() or "biometric" in text.lower():
        return ("Biometric Attendance/Access System",
                "Captures entries using fingerprint/biometric scans. Prevents proxy access, "
                "but needs secure template storage and spoof detection.")

    if "visitor" in text.lower() or "logbook" in text.lower():
        return ("Visitors Logbook",
                "Records guest entries manually or digitally. Prone to errors/falsification, "
                "limited forensic use unless digitized with ID validation.")

    if "policy" in text.lower() or "firewall" in text.lower() or "ids" in text.lower():
        return ("Security Policy/Config File",
                "Defines access, firewall, or IDS rules. Misconfigurations can expose systems; "
                "needs regular audits and least-privilege enforcement.")

    if "kernel" in text.lower() or "syslog" in text.lower() or "boot" in text.lower():
        return ("System Log File",
                "Captures OS and kernel events. Useful for detecting crashes or tampering, "
                "requires monitoring for repeated errors or anomalies.")

    if "failed password" in text.lower() or "authentication failure" in text.lower():
        return ("Authentication Log",
                "Tracks login attempts. Multiple failures suggest brute force; "
                "suspicious geolocations may indicate account compromise.")

    if "incident" in text.lower() or "breach" in text.lower():
        return ("Incident Report",
                "Documents security events and response actions. Reveals attack vectors and impact; "
                "should guide updates to security controls.")

    # Default - If none of the above rules matched then treat it as generic file.
    snippet = text[:100].replace("\n", " ") # return first 100 characters as a preview
    return (f"Generic {file_type.upper()} File",
            f"Extracted snippet: {snippet}...")