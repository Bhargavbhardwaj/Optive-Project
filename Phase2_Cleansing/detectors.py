import re   # regular expression
import logging

try:
    import spacy  # natural language processing library toolkit
    NLP = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except Exception:
    NLP = None
    HAS_SPACY = False

# high -recall regex patterns

RE_PATTERNS = {  # match the findings from this pattern
    "Email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "FULL_NAME": re.compile(r"\b([A-Z][a-z]+[\s\-]){1,2}[A-Z][a-z]+\b"),
    "NAME_WITH_TITLE": re.compile(r"\b(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s([A-Z][a-z]+[\s\-]){1,2}[A-Z][a-z]+\b"),

    "Phone": re.compile(r"\b(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{6,12}\b"),
    "IP": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "SSN_US": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "URL": re.compile(r"https?://[^\s]+"),
    "AADHAR_CARD" : re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "PAN_CARD": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "INDIAN_DISTRICT": re.compile(r"\b(?:District|Dist|Zilla)\s+[A-Za-z\s]+\b", re.IGNORECASE),
    "INDIAN_PINCODE": re.compile(r"\b\d{6}\b")


}

def detect_pii_in_text(text: str, use_spacy: bool = False):   # if want to use spacy than make it true

    detections = [] # creates an empty list to store all findings like emails, phNumb, names
    for name, pattern in RE_PATTERNS.items():
        for m in pattern.finditer(text):  # returns an iterator over all matches in the text
            detections.append({  # for each m, dictionary is appended
                "type":name,  # what type of PII
                "match":m.group(0),  # the actual text matched
                "start": m.start(), # character positions in the text
                "end": m.end(),
                "source": "regex"  # it says taht match came from regex detection
            })


    if use_spacy and HAS_SPACY and NLP is not None:  # only runs if spacy is installed and use_spacy is True and NLP is loaded properly

        try:
            doc = NLP(text)  # passes text into spacy's pipeline -->> returns a doc object with linguistic analysis
            for ent in doc.ents:  # loops over detedted named entities in the text
                if ent.label_ in ("PERSON", "ORG", "GPE", "LOC"):  # filters entities for people, org, place and location
                    detections.append({ # appends another detection dictionary
                        "type":ent.label_,
                        "match":ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "source": "spacy"
                    })
        except Exception as e:
            logging.warning("Spacy detection failed: %s", e)  # if spacy fails, logs a warning

    detections.sort(key=lambda d: d["start"]) # sorts all detections by their starting position in text
    return detections

