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


def extract_time(text: str) -> str | None:
    """
    Extract explicit times from text.

    Supported examples:
    - 5 PM
    - 5:00 PM
    - 17:00
    """

    patterns = [
        r"\b(\d{1,2}):(\d{2})\s*(AM|PM)\b",
        r"\b(\d{1,2})\s*(AM|PM)\b",
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b"
    ]

    for index, pattern in enumerate(patterns):
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        try:
            if index == 0:
                hour = int(match.group(1))
                minute = int(match.group(2))
                period = match.group(3).upper()

                if period == "PM" and hour != 12:
                    hour += 12
                elif period == "AM" and hour == 12:
                    hour = 0

            elif index == 1:
                hour = int(match.group(1))
                minute = 0
                period = match.group(2).upper()

                if period == "PM" and hour != 12:
                    hour += 12
                elif period == "AM" and hour == 12:
                    hour = 0

            else:
                hour = int(match.group(1))
                minute = int(match.group(2))

            return f"{hour:02d}:{minute:02d}"

        except ValueError:
            return None

    return None

def classify_task_type(text: str) -> str | None:
    """
    Classify the basic type of a student task or event.
    """

    text_lower = text.lower()

    if "assignment" in text_lower:
        return "assignment"

    if "exam" in text_lower or "examination" in text_lower:
        return "exam"

    if "quiz" in text_lower:
        return "quiz"

    if "project" in text_lower:
        return "project"

    if "viva" in text_lower:
        return "viva"

    if "class" in text_lower or "lecture" in text_lower:
        return "class"

    if "meeting" in text_lower:
        return "meeting"

    if "event" in text_lower:
        return "event"

    return None

def calculate_confidence(
    task_title: str | None,
    task_type: str | None,
    due_date: str | None,
    due_time: str | None
) -> float:
    """
    Calculate a simple baseline confidence score.

    Each successfully extracted component contributes
    to the overall confidence.
    """

    score = 0.0

    if task_title:
        score += 0.25

    if task_type:
        score += 0.25

    if due_date:
        score += 0.25

    if due_time:
        score += 0.25

    return round(score, 2)

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
    task_type = classify_task_type(text)
    due_date = extract_date(text)
    due_time = extract_time(text)
    confidence = calculate_confidence(
    task_title,
    task_type,
    due_date,
    due_time
)

    return {
        "task_title": task_title,
        "description": None,
        "task_type": task_type,
        "subject": None,
        "due_date": due_date,
        "due_time": due_time,
        "event_datetime": None,
        "source": source,
        "raw_text": raw_text,
        "date_time_expression": None,
        "confidence": confidence,
        "change_information": []
    }
