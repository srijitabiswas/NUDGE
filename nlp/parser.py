import spacy
import re
from datetime import datetime


nlp = spacy.blank("en")


def extract_task_title(text: str) -> str | None:
    """
    Extract a basic task title from a task-like message.
    """

    text = text.strip()

    if not text:
        return None

    title = re.sub(
        r"\s+(by|before|on|at)\s+.+$",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    return title if title else text


def extract_date(text: str) -> str | None:
    """
    Extract explicit dates from text.

    Supported examples:
    - 15th October
    - October 15
    - 15 October
    - 2026-10-15
    """

    current_year = datetime.now().year

    patterns = [
        r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b",
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        try:
            if pattern == patterns[0]:
                year, month, day = match.groups()
                date = datetime(
                    int(year),
                    int(month),
                    int(day)
                )

            elif match.group(1).isdigit():
                day = int(match.group(1))
                month = datetime.strptime(
                    match.group(2),
                    "%B"
                ).month

                date = datetime(
                    current_year,
                    month,
                    day
                )

            else:
                month = datetime.strptime(
                    match.group(1),
                    "%B"
                ).month
                day = int(match.group(2))

                date = datetime(
                    current_year,
                    month,
                    day
                )

            return date.strftime("%Y-%m-%d")

        except ValueError:
            return None

    return None


def parse_message(raw_text: str, source: str) -> dict:
    """
    Basic NLP message parser.
    """

    doc = nlp(raw_text)
    text = doc.text.strip()

    action_words = [
        "submit",
        "complete",
        "finish",
        "upload",
        "prepare",
        "attend",
        "register",
        "apply",
        "study",
        "revise",
        "solve",
        "read"
    ]

    is_task = any(
        text.lower().startswith(word)
        for word in action_words
    )

    task_title = extract_task_title(text) if is_task else None
    due_date = extract_date(text)

    return {
        "task_title": task_title,
        "description": None,
        "task_type": None,
        "subject": None,
        "due_date": due_date,
        "due_time": None,
        "event_datetime": None,
        "source": source,
        "raw_text": raw_text,
        "date_time_expression": None,
        "confidence": 0.0,
        "change_information": []
    }