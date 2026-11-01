"""OCR-to-NLP adapter (roadmap Step 36).

Connects the OCR module's JSON output to ``parse_message``. It does not change
the parser or the shared NLP contract: the NLP result is returned exactly as
``parse_message`` produced it, and the OCR details are returned next to it,
never inside it.

An OCR record (one JSON file per screenshot) looks like this:

    {
        "source": "screenshot 9.jpeg",        image file name
        "raw_text": "...",                    original OCR text (not used here)
        "cleaned_text": "...",                the text given to the parser
        "overall_confidence": 0.6024,         average OCR confidence, or null
        "confidence": [{"text": "...", "score": 0.65}, ...]   per text line
    }

Usage:

    from nlp.ocr_adapter import parse_ocr_file, parse_ocr_record

    result = parse_ocr_file("shot.json", reference_date=datetime(2026, 10, 28))
    result["task"]   # normal NLP output; its "source" is "Screenshot/OCR"
    result["ocr"]    # image_filename, overall_confidence, line_confidences

The NLP ``confidence`` (how complete the parsed fields are) and the OCR
confidence (how sure the OCR engine was about the text) are different things.
They are kept in different places and never mixed.
"""

import json
import math
from datetime import date, datetime
from pathlib import Path

from nlp.parser import parse_message

OCR_SOURCE = "Screenshot/OCR"
REQUIRED_FIELDS = ("source", "cleaned_text", "overall_confidence", "confidence")


class OCRRecordError(ValueError):
    """Raised when an OCR record is missing a field or has an invalid value."""


def _is_confidence(value):
    """True for a real number from 0 to 1. Booleans, NaN and infinity are not."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value) and 0 <= value <= 1


def _validate(record):
    """Check an OCR record; raise OCRRecordError naming the problem field."""
    if not isinstance(record, dict):
        raise OCRRecordError(
            f"OCR record must be a dictionary, got {type(record).__name__}"
        )

    for field in REQUIRED_FIELDS:
        if field not in record:
            raise OCRRecordError(f"OCR record is missing required field '{field}'")

    source = record["source"]
    if not isinstance(source, str) or not source.strip():
        raise OCRRecordError("OCR field 'source' must be a non-empty string")

    if not isinstance(record["cleaned_text"], str):
        raise OCRRecordError(
            "OCR field 'cleaned_text' must be a string, "
            f"got {type(record['cleaned_text']).__name__}"
        )

    overall = record["overall_confidence"]
    if overall is not None and not _is_confidence(overall):
        raise OCRRecordError(
            "OCR field 'overall_confidence' must be null or a number from 0 to 1, "
            f"got {overall!r}"
        )

    lines = record["confidence"]
    if not isinstance(lines, list):
        raise OCRRecordError(
            f"OCR field 'confidence' must be a list, got {type(lines).__name__}"
        )
    for index, item in enumerate(lines):
        if not isinstance(item, dict):
            raise OCRRecordError(
                f"OCR field 'confidence'[{index}] must be a dictionary "
                "with 'text' and 'score'"
            )
        if not isinstance(item.get("text"), str):
            raise OCRRecordError(
                f"OCR field 'confidence'[{index}] needs a string 'text'"
            )
        if not _is_confidence(item.get("score")):
            raise OCRRecordError(
                f"OCR field 'confidence'[{index}] 'score' must be a number "
                f"from 0 to 1, got {item.get('score')!r}"
            )


def parse_ocr_record(
    record: dict,
    reference_date: datetime | date | None = None,
) -> dict:
    """Parse one OCR record and return ``{"task": ..., "ocr": ...}``.

    ``task`` is the unchanged ``parse_message`` result for ``cleaned_text``
    with source ``"Screenshot/OCR"``. ``reference_date`` is passed straight
    through to the parser. ``ocr`` keeps the image file name, the overall OCR
    confidence (or None) and a copy of the per-line scores.

    Empty OCR text is allowed: the parser then returns its normal empty
    "general notice" result and the OCR details are still returned.
    Raises OCRRecordError if the record is invalid.
    """
    _validate(record)

    task = parse_message(record["cleaned_text"], OCR_SOURCE, reference_date)
    ocr = {
        "image_filename": record["source"],
        "overall_confidence": record["overall_confidence"],
        "line_confidences": [
            {"text": item["text"], "score": item["score"]}
            for item in record["confidence"]
        ],
    }
    return {"task": task, "ocr": ocr}


def parse_ocr_file(
    path: str | Path,
    reference_date: datetime | date | None = None,
) -> dict:
    """Load one OCR JSON file and parse it with :func:`parse_ocr_record`."""
    path = Path(path)
    try:
        with open(path, encoding="utf-8") as handle:
            record = json.load(handle)
    except json.JSONDecodeError as error:
        raise OCRRecordError(f"{path.name} is not valid JSON: {error}") from error
    return parse_ocr_record(record, reference_date)
