"""Best-effort field extraction from OCR text on an arbitrary real
document: regex/keyword matching over whatever core/realdoc/ocr.py
returned, not a learned extractor. Every field is reported EXTRACTED /
UNCERTAIN / NOT_DETECTED with a confidence bucket -- never a fabricated
value for a field that wasn't actually found.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from core.realdoc.ocr import OcrWord

_MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
           "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}

_DATE_PATTERNS = [
    r"\b(\d{1,2})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+(\d{4})\b",
    r"\b(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})\b",     # 2004-08-14 (ISO-ish)
    r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})\b",   # 14/08/2004, 14-08-04
]

_DOC_NUMBER_PATTERN = re.compile(r"\b[A-Z]{0,3}[0-9]{6,12}\b")

_LABEL_HINTS: dict[str, list[str]] = {
    "name": ["NAME", "SURNAME", "GIVEN NAME"],
    "date_of_birth": ["DATE OF BIRTH", "DOB", "BIRTH"],
    "document_number": ["PASSPORT NO", "DOCUMENT NO", "ID NO", "REGISTRATION NO", "ROLL NO", "NUMBER"],
    "date_of_issue": ["DATE OF ISSUE", "ISSUE DATE", "ISSUED"],
    "date_of_expiry": ["DATE OF EXPIRY", "EXPIRY", "VALID UNTIL", "VALID UPTO"],
    "nationality": ["NATIONALITY"],
    "gender": ["SEX", "GENDER"],
    "institution": ["UNIVERSITY", "COLLEGE", "INSTITUTE", "BOARD"],
}
_ALL_FIELD_KEYS = tuple(_LABEL_HINTS.keys())
_GENDER_TOKENS = ("MALE", "FEMALE", "TRANSGENDER", "M", "F")
_ALPHA_RUN = re.compile(r"[A-Z]{2,}")


@dataclass
class ExtractedField:
    value: str
    status: str        # "EXTRACTED" | "UNCERTAIN" | "NOT_DETECTED"
    confidence: str     # "HIGH" | "MEDIUM" | "LOW" | "-"
    source: str = ""    # the OCR line this came from, for audit


def _confidence_bucket(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.60:
        return "MEDIUM"
    return "LOW"


def _try_parse_date(text_upper: str) -> str:
    """Returns an ISO date string, or "" if nothing plausible was found."""
    import datetime as _dt
    for pat in _DATE_PATTERNS:
        m = re.search(pat, text_upper)
        if not m:
            continue
        g = m.groups()
        try:
            if g[1] in _MONTHS:
                d, mon, y = int(g[0]), _MONTHS[g[1]], int(g[2])
            elif len(g[0]) == 4:
                y, mon, d = int(g[0]), int(g[1]), int(g[2])
            else:
                d, mon, y = int(g[0]), int(g[1]), int(g[2])
                if y < 100:
                    y += 2000 if y < 50 else 1900
            return _dt.date(y, mon, d).isoformat()
        except ValueError:
            continue
    return ""


def extract_fields(words: list[OcrWord]) -> dict[str, ExtractedField]:
    """One pass over OCR'd lines: find a label keyword, then take the value
    from the remainder of that same line, or the very next line if the
    label line has no residual text -- documents commonly print a label and
    its value as two separately-boxed OCR regions, stacked vertically."""
    lines = [w.text for w in words]
    upper_lines = [l.upper() for l in lines]
    fields: dict[str, ExtractedField] = {}

    all_hints = [h for hints in _LABEL_HINTS.values() for h in hints]

    for i, line in enumerate(upper_lines):
        for field_key, hints in _LABEL_HINTS.items():
            if field_key in fields:
                continue
            hit = next((h for h in hints if h in line), None)
            if hit is None:
                continue
            remainder = line.split(hit, 1)[1].strip(" :-")
            next_line = upper_lines[i + 1] if i + 1 < len(upper_lines) else ""
            # A short/empty remainder means this OCR box was just the label;
            # the value is very likely the next box down -- UNLESS that next
            # box is itself another field's label (a document with several
            # stacked label/value pairs whose watermark or layout starved
            # this label of its own value reads as NOT_DETECTED, not as
            # someone else's label text).
            if len(remainder) >= 2:
                candidate = remainder
            elif next_line and not any(h in next_line for h in all_hints):
                candidate = next_line
            else:
                candidate = ""
            if not candidate:
                continue
            conf = words[i].confidence

            if field_key.startswith("date_of"):
                parsed = _try_parse_date(candidate)
                if parsed:
                    fields[field_key] = ExtractedField(parsed, "EXTRACTED", _confidence_bucket(conf), lines[i])
            elif field_key == "document_number":
                m = _DOC_NUMBER_PATTERN.search(candidate)
                if m:
                    fields[field_key] = ExtractedField(m.group(0), "EXTRACTED", _confidence_bucket(conf), lines[i])
            elif field_key == "gender":
                token = candidate.strip().split()[0] if candidate.strip() else ""
                if token in _GENDER_TOKENS:
                    fields[field_key] = ExtractedField(token, "EXTRACTED", _confidence_bucket(conf), lines[i])
            else:
                # A free-text field (name/nationality/institution) grabbed
                # from a neighbouring OCR box that turns out to be numbers-
                # only (a stray date/ID fragment, the same watermark-driven
                # misread that motivated the gender check above) is reported
                # NOT_DETECTED rather than shown as a bogus "name".
                value = candidate[:60].strip()
                if value and _ALPHA_RUN.search(value):
                    status = "EXTRACTED" if conf >= 0.60 else "UNCERTAIN"
                    fields[field_key] = ExtractedField(value, status, _confidence_bucket(conf), lines[i])
            break

    for key in _ALL_FIELD_KEYS:
        fields.setdefault(key, ExtractedField("", "NOT_DETECTED", "-", ""))
    return fields
