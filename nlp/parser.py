import spacy


nlp = spacy.blank("en")


def parse_message(raw_text: str, source: str) -> dict:
    """
    Basic NLP message parser.

    Takes raw student text and its source, then returns
    the initial structured representation.
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

    task_title = text if is_task else None

    return {
        "task_title": task_title,
        "description": None,
        "task_type": None,
        "subject": None,
        "due_date": None,
        "due_time": None,
        "event_datetime": None,
        "source": source,
        "raw_text": raw_text,
        "date_time_expression": None,
        "confidence": 0.0,
        "change_information": []
    }
import spacy
import re


nlp = spacy.blank("en")


def extract_task_title(text: str) -> str | None:
    """
    Extract a basic task title from a task-like message.
    """

    text = text.strip()

    if not text:
        return None

    # Remove common deadline phrases from the end.
    title = re.sub(
        r"\s+(by|before|on|at)\s+.+$",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    return title if title else text


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

    return {
        "task_title": task_title,
        "description": None,
        "task_type": None,
        "subject": None,
        "due_date": None,
        "due_time": None,
        "event_datetime": None,
        "source": source,
        "raw_text": raw_text,
        "date_time_expression": None,
        "confidence": 0.0,
        "change_information": []
    }