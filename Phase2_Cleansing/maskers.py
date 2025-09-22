# here PIIs are either masked or removed to clean the file

from typing import Tuple, Dict, List

def mask_text(
        text : str,  # original text
        detections : List[dict], # output of detectors from [detect_pii_in_text] (with start, end, match from previous file)
        action : str = "mask"   # replace with remove to delete the text
) -> str: # returns a new string with masked PII
    out = []
    last_idx = 0  # # keeps track of where we last stopped copying
    for d in detections:
        s, e = d["start"], d["end"]  # start and end indices of PII span
        if s < last_idx: # skips overlapping matches
            continue
        out.append(text[last_idx:s])  # copy normal text up to the start of this detection

        if action == "mask":
            replacement = "[REDACTED]"
        elif action == "remove":
            replacement = ""  # drop it completely
        else:
            replacement = "[REDACTED]"

        out.append(replacement)  # add replacement into output list
        last_idx = e  # updates the index forward so the next chunk starts after this detection

    out.append(text[last_idx:])  # add the remaining part of the text after last detection
    return "".join(out)  # merges everything into final cleaned text


