"""Rule-based NLP parser for student messages and notices.

Roadmap Phase 2, Steps 14-21. It turns one unstructured message into the
shared structured data contract described in docs/NLP_INTERFACE.md:

    parse_message(raw_text, source, reference_date) -> dict

Fields owned by the task/storage layer (task_id, due_datetime, status,
created_at, completed_at) are never produced here. Unknown information is
always None (never guessed) and change_information is always a list.
"""

import re
from datetime import date, datetime, timedelta

import spacy

nlp = spacy.blank("en")


# --------------------------------------------------
# SMALL HELPERS
# --------------------------------------------------

def _capitalise(text: str) -> str:
    return text[:1].upper() + text[1:]


def _as_date(value) -> date:
    """Accept a datetime, a date or None (None means today)."""
    if value is None:
        return datetime.now().date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise TypeError("reference_date must be a datetime, a date or None")


_ABBREVIATION_RE = re.compile(
    r"\b(jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|dr|mr|mrs|ms|prof|no|st)\.",
    re.IGNORECASE,
)


def _split_sentences(text: str) -> list[str]:
    """Split on . ! ? ; and new lines, but not after "Nov." or "Dr."."""
    protected = _ABBREVIATION_RE.sub(lambda m: m.group(1) + "\x00", text.strip())
    parts = re.split(r"(?<=[.!?])\s+|;\s+|\n+", protected)
    return [part.replace("\x00", ".").strip() for part in parts if part.strip()]


# --------------------------------------------------
# SUBJECT EXTRACTION
# --------------------------------------------------

# Known course names. Extend this list with the real course list.
SUBJECTS = [
    "Machine Learning",
    "Data Structures",
    "Operating Systems",
    "Computer Networks",
    "Software Engineering",
    "Data Mining",
    "Artificial Intelligence",
    "Discrete Mathematics",
    "Computer Architecture",
    "Web Technologies",
    "Statistics",
    "Physics",
    "Smart Campus",
    "Final-year project",
    "DBMS",
    "Network Security",
    "Cyber Security",
    "Information Security",
    "Compiler Design",
    "Computer Graphics",
    "Theory of Computation",
    "Database Management Systems",
    "Cloud Computing",
    "Deep Learning",
    "Natural Language Processing",
    "Digital Logic",
    "Engineering Mathematics",
    "Mathematics",
    "Chemistry",
    "Internet of Things",
    "Big Data",
    "Image Processing",
]

_SUBJECT_STOPWORDS = {
    "please", "kindly", "reminder", "notice", "update", "urgent", "important",
    "note", "dear", "hello", "hi", "hey", "students", "all", "everyone",
    "submit", "complete", "finish", "upload", "prepare", "attend", "bring",
    "register", "apply", "study", "revise", "solve", "read", "the", "our",
    "your", "a", "an", "this", "that", "new", "today", "tomorrow", "tonight",
    "next", "also", "and", "for", "on", "in", "at", "by", "we", "you", "it",
    "there", "is", "are", "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday", "january", "february", "march", "april",
    "may", "june", "july", "august", "september", "october", "november",
    "december",
}

_SUBJECT_MODIFIERS = {
    "final", "internal", "practical", "lab", "mid-sem", "mid-semester",
    "end-sem", "end-semester", "online", "weekly", "unit", "class", "semester",
}

# "<Capitalised Words> [modifier] assignment/quiz/exam/..." -> the words are
# the subject. Used only when the name is not in SUBJECTS.
_SUBJECT_PHRASE_RE = re.compile(
    r"([A-Z][\w&-]*(?:\s+(?:(?:of|and)\s+)?[A-Z][\w&-]*){0,3})"
    r"\s+(?:(?i:practical|lab|mid-semester|mid-sem|end-semester|end-sem|"
    r"internal|final|weekly|online|unit|class)\s+)*"
    r"(?i:assignment|quiz|exam|examination|viva|test|lab|lecture|class|"
    r"project|practical|tutorial)\b"
)


def _subject_from_phrase(text: str) -> str | None:
    for match in _SUBJECT_PHRASE_RE.finditer(text):
        words = match.group(1).split()
        while words and words[0].lower() in _SUBJECT_STOPWORDS:
            words.pop(0)
        while words and words[-1].lower() in _SUBJECT_MODIFIERS:
            words.pop()
        if words and len(words) <= 4 and words[-1].lower() not in _SUBJECT_STOPWORDS:
            return " ".join(words)
    return None


def extract_subject(text: str) -> str | None:
    """Extract a subject: a known course name, else a capitalised phrase."""
    known = None
    for subject in sorted(SUBJECTS, key=len, reverse=True):
        if re.search(rf"(?<!\w){re.escape(subject)}(?!\w)", text, re.IGNORECASE):
            known = subject
            break

    phrase = _subject_from_phrase(text)
    if known is None:
        return phrase

    # "Organic Chemistry" is a better answer than the known word "Chemistry".
    if (
        phrase
        and len(phrase.split()) <= 3
        and phrase.lower().endswith(" " + known.lower())
    ):
        return phrase
    return known


# --------------------------------------------------
# TASK TYPE
# --------------------------------------------------

def classify_task_type(text: str) -> str | None:
    """Classify a task or scheduled academic activity."""
    text_lower = text.lower()

    if re.search(r"\bassignment\b", text_lower):
        return "assignment"
    if re.search(r"\bquiz\b", text_lower):
        return "quiz"
    if re.search(r"\bviva\b", text_lower):
        return "viva"
    if re.search(r"\b(exam|examination)\b", text_lower):
        return "exam"
    if re.search(r"\bmeeting\b", text_lower):
        return "meeting"
    if re.search(r"\b(class|lecture)\b", text_lower):
        return "class"
    if re.search(r"\bproject\b", text_lower):
        return "project"
    if re.search(
        r"\b(seminar|workshop|cultural fest|college fest|festival)\b",
        text_lower,
    ):
        return "event"
    return None


# --------------------------------------------------
# MESSAGE CATEGORY (task / event / general notice)
# --------------------------------------------------

# An explicit action means the message is a task, even if it mentions an exam.
_EXPLICIT_ACTION_RE = re.compile(
    r"\b(?:submit|complete|finish|upload|prepare|study|revise|solve|read|"
    r"bring|register|apply|pay|collect)\b"
)
# "must be submitted", "has to be uploaded" ...
_PASSIVE_ACTION_RE = re.compile(
    r"\b(?:must|should|need(?:s)?\s+to|has\s+to|have\s+to|is\s+to|are\s+to|to)"
    r"\s+be\s+(?:submitted|uploaded|completed|finished|prepared)\b"
)
_ATTEND_RE = re.compile(r"\battend\b")
_DEADLINE_WORD_RE = re.compile(r"\b(?:deadline|due)\b(?!\s+to\b)")
_EVENT_KEYWORD_RE = re.compile(
    r"\b(?:meeting|seminar|workshop|lecture|class|viva|cultural fest|"
    r"college fest|festival|quiz|exam|examination)\b"
)
# Step 40: poster and notice words. They announce an event only when the text
# also says WHEN (a date or a time); "talk" must look like a noun ("an invited
# talk", "talk on ..."), because "talk to your advisor" is an instruction.
_SCHEDULED_EVENT_RE = re.compile(
    r"\b(?:webinar|session|debate|distribution|orientation|hackathon)\b"
    r"|\b(?:an?|the|invited|guest|expert)\s+(?:\w+\s+)?talk\b|\btalk\s+on\b"
)

_NOTICE_PATTERNS = [
    re.compile(
        r"\b(?:timetable|time table|datesheet|schedule|results?|marks|grades|"
        r"admit cards?|hall tickets?)\s+(?:has|have)\s+been\s+"
        r"(?:published|released|declared|uploaded|announced|posted)\b"
    ),
    re.compile(
        r"\b(?:timetable|time table|datesheet|schedule|results?)\b.{0,40}"
        r"\b(?:will be|to be)\s+(?:published|released|declared|announced)\b"
    ),
    re.compile(r"\b(?:will\s+remain|will\s+be|is|are)\s+closed\b"),
    re.compile(r"\bholidays?\b"),
    re.compile(
        r"\b(?:registration|admissions?|enrolment|enrollment)\s+"
        r"(?:opens?|begins?|starts?)\b"
    ),
]


def _has_task_signal(text_lower: str) -> bool:
    return bool(
        _EXPLICIT_ACTION_RE.search(text_lower)
        or _PASSIVE_ACTION_RE.search(text_lower)
        or _ATTEND_RE.search(text_lower)
        or _DEADLINE_WORD_RE.search(text_lower)
    )


def is_general_notice(text: str) -> bool:
    """
    Identify announcements that should not become tasks or events
    (a published timetable, a closure, a registration opening ...).
    A message that asks the student to do something is never a notice.
    """
    text_lower = text.lower()

    if _has_task_signal(text_lower):
        return False

    return any(pattern.search(text_lower) for pattern in _NOTICE_PATTERNS)


def is_event_message(text: str) -> bool:
    """
    Identify scheduled events, rather than tasks with deadlines.
    """
    text_lower = text.lower()

    if not (_EVENT_KEYWORD_RE.search(text_lower) or _scheduled_event_word(text)):
        return False

    # An explicit task action generally indicates a task, even when the
    # task is called a quiz or an exam.
    if _EXPLICIT_ACTION_RE.search(text_lower) or _PASSIVE_ACTION_RE.search(text_lower):
        return False

    return True


# --------------------------------------------------
# DATE EXTRACTION
# --------------------------------------------------

_MONTH_NUMBERS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH = (
    "january|february|march|april|may|june|july|august|september|october|"
    "november|december|sept|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
)
_WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

_ISO_DATE_RE = re.compile(r"\b(?P<y>\d{4})-(?P<mo>\d{1,2})-(?P<d>\d{1,2})\b")
_DAY_MONTH_RE = re.compile(
    rf"\b(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<m>{_MONTH})(?![a-z])\.?"
    r"(?:\s*,?\s*(?P<y>20\d{2})\b)?",
    re.IGNORECASE,
)
_MONTH_DAY_RE = re.compile(
    rf"\b(?P<m>{_MONTH})(?![a-z])\.?\s+(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\b"
    r"(?!\s*(?:am|pm)\b)(?![:.]\d)(?:\s*,?\s*(?P<y>20\d{2})\b)?",
    re.IGNORECASE,
)
# "4th and 5th April 2019": a range of days. The START day is the date.
_DAY_RANGE_RE = re.compile(
    rf"\b(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\s*(?:and|&|to|-|\u2013|\u2014)\s*"
    rf"\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<m>{_MONTH})(?![a-z])\.?"
    r"(?:\s*,?\s*(?P<y>20\d{2})\b)?",
    re.IGNORECASE,
)
_TODAY_TOMORROW_RE = re.compile(r"\b(?:tomorrow|today|tonight)\b", re.IGNORECASE)
# Step 38: more ways to say a day.
_AFTER_TOMORROW_RE = re.compile(r"(?:\bthe\s+)?\bday\s+after\s+tomorrow\b", re.IGNORECASE)
_NUMBER_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12,
}
_IN_N_RE = re.compile(
    r"\bin\s+(?P<n>\d{1,3}|a|an|one|two|three|four|five|six|seven|eight|nine|"
    r"ten|eleven|twelve)\s+(?P<u>days?|weeks?)\b",
    re.IGNORECASE,
)
# "Friday", "this Friday", "next Friday", "next week on Friday"
_WEEKDAY_RE = re.compile(
    r"\b(?:(?P<q>next|this|coming)\s+(?:week\s*,?\s*(?:on\s+)?)?)?"
    r"(?P<wd>monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.IGNORECASE,
)
_NEXT_WEEK_WEEKDAY_RE = re.compile(
    r"\bnext\s+week\s*,?\s*(?:on\s+)?(?:monday|tuesday|wednesday|thursday|"
    r"friday|saturday|sunday)\b",
    re.IGNORECASE,
)
_DAY_PART_RE = re.compile(r"\s+(?:night|evening|morning|afternoon)\b", re.IGNORECASE)
_MIDNIGHT_BEFORE_RE = re.compile(r"\bmidnight\s+(?:on\s+|of\s+)?$", re.IGNORECASE)
_MIDNIGHT_AFTER_RE = re.compile(r"^\s*(?:at\s+|by\s+)?midnight\b", re.IGNORECASE)
# DD/MM/YYYY (Indian order, never swapped)
_SLASH_DATE_RE = re.compile(
    r"(?<![\d/])(?P<d>\d{1,2})/(?P<mo>\d{1,2})/(?P<y>(?:19|20)\d{2})(?![\d/])"
)
_NEXT_WEEK_RE = re.compile(r"\bnext week\b", re.IGNORECASE)
_VAGUE_PERIOD_RE = re.compile(
    r"\b(?:next|this|coming)\s+(?:week|month)\b", re.IGNORECASE
)


def _resolve_day_month(day: int, month: int, ref: date, year: int | None):
    """A date written without a year: take the year that is nearest to the
    reference date (so 5 January written in December means next year)."""
    if year is not None:
        try:
            return date(year, month, day)
        except ValueError:
            return None

    best = None
    for candidate_year in (ref.year - 1, ref.year, ref.year + 1):
        try:
            candidate = date(candidate_year, month, day)
        except ValueError:
            continue
        delta = (candidate - ref).days
        key = (abs(delta), delta < 0)
        if best is None or key < best[0]:
            best = (key, candidate)
    return best[1] if best else None


def _absolute_dates(text: str, ref: date) -> list[tuple[int, int, date]]:
    """Every explicit calendar date as (start, end, date), left to right."""
    found = []

    for match in _ISO_DATE_RE.finditer(text):
        try:
            found.append((
                match.start(), match.end(),
                date(int(match["y"]), int(match["mo"]), int(match["d"])),
            ))
        except ValueError:
            continue

    for match in _SLASH_DATE_RE.finditer(text):
        try:
            found.append((
                match.start(), match.end(),
                date(int(match["y"]), int(match["mo"]), int(match["d"])),
            ))
        except ValueError:
            continue  # 31/02/2026 or 12/25/2026: not a real DD/MM/YYYY date

    for pattern in (_DAY_RANGE_RE, _DAY_MONTH_RE, _MONTH_DAY_RE):
        for match in pattern.finditer(text):
            if pattern is _DAY_RANGE_RE and _CHANGE_VERB_RE.search(
                text[max(0, match.start() - 60):match.start()]
            ):
                continue  # "moved from 8 to 12 November" is a change, not a range
            resolved = _resolve_day_month(
                int(match["d"]),
                _MONTH_NUMBERS[match["m"].lower()],
                ref,
                int(match["y"]) if match["y"] else None,
            )
            if resolved:
                found.append((match.start(), match.end(), resolved))

    found.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    kept = []
    for item in found:
        if kept and item[0] < kept[-1][1]:
            continue  # overlaps a date that was already accepted
        kept.append(item)
    return kept


def _weekday_date(weekday: str, qualifier: str | None, ref: date) -> date:
    """plain "Friday": the nearest upcoming one (a week away if today is Friday).
    "this/coming Friday": the upcoming one (today counts).
    "next Friday": Friday of the FOLLOWING week (weeks run Monday to Sunday)."""
    target = _WEEKDAYS[weekday.lower()]
    qualifier = (qualifier or "").lower()
    if qualifier == "next":
        return ref - timedelta(days=ref.weekday()) + timedelta(days=7 + target)
    ahead = (target - ref.weekday()) % 7
    if qualifier in ("this", "coming"):
        return ref + timedelta(days=ahead)
    return ref + timedelta(days=ahead or 7)


def _midnight_shift(text: str, start: int, end: int) -> int:
    """"midnight tonight", "tomorrow midnight", "midnight on Sunday" mean 00:00
    at the END of that day, i.e. the next calendar day."""
    if _MIDNIGHT_BEFORE_RE.search(text[max(0, start - 20):start]):
        return 1
    if _MIDNIGHT_AFTER_RE.match(text[end:end + 20]):
        return 1
    return 0


def _relative_dates(text: str, ref: date) -> list[tuple[int, int, date]]:
    found = []

    def free(start, end):
        return not any(start < f_end and f_start < end for f_start, f_end, _ in found)

    def add(start, end, day):
        found.append((start, end, day + timedelta(days=_midnight_shift(text, start, end))))

    for match in _AFTER_TOMORROW_RE.finditer(text):
        add(match.start(), match.end(), ref + timedelta(days=2))

    for match in _IN_N_RE.finditer(text):
        count = match["n"].lower()
        count = int(count) if count.isdigit() else _NUMBER_WORDS[count]
        days = count * (7 if match["u"].lower().startswith("week") else 1)
        add(match.start(), match.end(), ref + timedelta(days=days))

    for match in _TODAY_TOMORROW_RE.finditer(text):
        if not free(match.start(), match.end()):
            continue  # the "tomorrow" inside "day after tomorrow"
        word = match.group(0).lower()
        end = match.end()
        if word == "tomorrow":
            part = _DAY_PART_RE.match(text, end)
            end = part.end() if part else end
        add(match.start(), end, ref + timedelta(days=1 if word == "tomorrow" else 0))

    for match in _WEEKDAY_RE.finditer(text):
        part = _DAY_PART_RE.match(text, match.end())  # "Sunday night"
        end = part.end() if part else match.end()
        add(match.start(), end, _weekday_date(match["wd"], match["q"], ref))

    return found


def _find_date(text: str, ref: date):
    """Return (YYYY-MM-DD, start, end) for the date the message is about.

    An explicit calendar date beats a relative word, and the last explicit
    date wins (so "moved from 8 November to 12 November" gives 12 November).
    """
    absolute = _absolute_dates(text, ref)
    if absolute:
        start, end, found = max(absolute, key=lambda item: item[0])
        return found.isoformat(), start, end

    if _NEXT_WEEK_RE.search(text) and not _NEXT_WEEK_WEEKDAY_RE.search(text):
        return None  # too vague to be a specific date

    relative = _relative_dates(text, ref)
    if relative:
        start, end, found = max(relative, key=lambda item: item[0])
        return found.isoformat(), start, end

    return None


def extract_date(
    text: str,
    reference_date: datetime | date | None = None,
) -> str | None:
    """Extract explicit and relative dates as YYYY-MM-DD."""
    hit = _find_date(text, _as_date(reference_date))
    return hit[0] if hit else None


# --------------------------------------------------
# TIME EXTRACTION
# --------------------------------------------------

_MERIDIEM = r"(?P<p>a\.?m\.?|p\.?m\.?)(?![a-z])"
_AMPM_RE = re.compile(
    r"(?<![\d:.])(?P<h>\d{1,2})(?:[:.](?P<m>\d{2}))?\s*" + _MERIDIEM,
    re.IGNORECASE,
)
# "4.30-5.30 PM": one am/pm shared by both ends of a range.
_SHARED_RANGE_RE = re.compile(
    r"(?<![\d:.])(?P<h1>\d{1,2})[:.](?P<m1>\d{2})\s*(?:-|\u2013|\u2014|to|till|until)\s*"
    r"(?P<h2>\d{1,2})(?:[:.](?P<m2>\d{2}))?\s*" + _MERIDIEM,
    re.IGNORECASE,
)
_24H_RE = re.compile(
    r"(?<![\d:-])(?P<h>[01]?\d|2[0-3]):(?P<m>[0-5]\d)(?!\d)(?!\s*(?:am|pm)\b)",
    re.IGNORECASE,
)
_NOON_RE = re.compile(r"\bnoon\b", re.IGNORECASE)
_MIDNIGHT_RE = re.compile(r"\bmidnight\b", re.IGNORECASE)
_RANGE_GAP_RE = re.compile(r"^\s*(?:to|till|until|-|–|—)\s*$", re.IGNORECASE)
_CHANGE_VERB_RE = re.compile(
    r"\b(rescheduled|postponed|preponed|moved|shifted|extended|advanced|changed)\b",
    re.IGNORECASE,
)


def _to_24h(hour: int, minute: int, pm: bool) -> str:
    if pm and hour != 12:
        hour += 12
    elif not pm and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def _time_matches(text: str) -> list[tuple[int, int, str]]:
    found = []
    taken = []  # spans already used by a shared-meridiem range

    for match in _SHARED_RANGE_RE.finditer(text):
        first, last = int(match["h1"]), int(match["h2"])
        minute1, minute2 = int(match["m1"]), int(match["m2"] or 0)
        if not (1 <= first <= 12 and 1 <= last <= 12 and minute1 <= 59 and minute2 <= 59):
            continue
        pm = match["p"].lower().startswith("p")
        # "11.00-1.00 PM" and "10.00-12.00 PM" start in the morning.
        start_pm = pm and (first == 12 or not (first > last or last == 12))
        found.append((match.start(), match.end(), _to_24h(first, minute1, start_pm)))
        taken.append((match.start(), match.end()))

    def free(start, end):
        return not any(start < t_end and t_start < end for t_start, t_end in taken)

    for match in _AMPM_RE.finditer(text):
        hour = int(match["h"])
        minute = int(match["m"] or 0)
        if not 1 <= hour <= 12 or minute > 59 or not free(match.start(), match.end()):
            continue
        found.append((
            match.start(), match.end(),
            _to_24h(hour, minute, match["p"].lower().startswith("p")),
        ))

    for match in _24H_RE.finditer(text):
        if free(match.start(), match.end()):
            found.append((
                match.start(), match.end(),
                f"{int(match['h']):02d}:{match['m']}",
            ))

    for match in _NOON_RE.finditer(text):
        if free(match.start(), match.end()):
            found.append((match.start(), match.end(), "12:00"))

    for match in _MIDNIGHT_RE.finditer(text):
        if free(match.start(), match.end()):
            found.append((match.start(), match.end(), "00:00"))

    found.sort(key=lambda item: item[0])
    return found


def _time_items(text: str) -> list[tuple[int, int, str]]:
    """Time matches, with a "10 AM to 12 PM" range merged into one item that
    keeps the START time. A range written as a change ("moved from 3 PM to
    5 PM") is left as two times so the new (last) time wins."""
    matches = _time_matches(text)
    items = []
    index = 0
    while index < len(matches):
        start, end, value = matches[index]
        is_range = (
            index + 1 < len(matches)
            and _RANGE_GAP_RE.match(text[end:matches[index + 1][0]])
            and not _CHANGE_VERB_RE.search(text[max(0, start - 40):start])
        )
        if is_range:
            items.append((start, matches[index + 1][1], value))
            index += 2
        else:
            items.append((start, end, value))
            index += 1
    return items


def _find_time(text: str, first: bool = False):
    """Return (HH:MM, start, end) for the last time mentioned, or None.
    A notice or poster (first=True) gives the START time, i.e. the first one."""
    items = _time_items(text)
    if not items:
        return None
    start, end, value = items[0] if first else items[-1]
    return value, start, end


def extract_time(text: str) -> str | None:
    """Extract a time and normalize it to HH:MM."""
    hit = _find_time(text)
    return hit[0] if hit else None


# --------------------------------------------------
# DATE-TIME EXPRESSION
# --------------------------------------------------

def _tidy(expression: str) -> str:
    return expression.strip(" .,;:")


def _build_expression(text: str, date_hit, time_hit) -> str | None:
    """The literal date/time words from the message, e.g.
    "15th October at 5:00 PM" or "tomorrow at 11:59 PM"."""
    spans = []
    if date_hit:
        spans.append((date_hit[1], date_hit[2]))
    if time_hit:
        spans.append((time_hit[1], time_hit[2]))

    if not spans:
        vague = _VAGUE_PERIOD_RE.search(text)
        return vague.group(0) if vague else None

    spans.sort()
    if len(spans) == 1:
        return _tidy(text[spans[0][0]:spans[0][1]])

    (start_a, end_a), (start_b, end_b) = spans
    gap = text[end_a:start_b]
    if len(gap) <= 15 and not re.search(r"[.;!?\n]", gap):
        return _tidy(text[start_a:end_b])
    return f"{_tidy(text[start_a:end_a])}, {_tidy(text[start_b:end_b])}"


# --------------------------------------------------
# TASK TITLE EXTRACTION
# --------------------------------------------------

_PASSIVE_TITLE_RE = re.compile(
    r"^(?P<obj>.+?)\s+(?:must|should|needs?\s+to|has\s+to|have\s+to|is\s+to|"
    r"are\s+to)\s+be\s+(?P<pp>submitted|uploaded|completed|finished|prepared)\b",
    re.IGNORECASE,
)
_PASSIVE_VERBS = {
    "submitted": "Submit", "uploaded": "Upload", "completed": "Complete",
    "finished": "Finish", "prepared": "Prepare",
}
_MEETING_TITLE_RE = re.compile(
    r"^(?:the\s+|our\s+|a\s+)?(?P<kind>[\w-]+)\s+meeting\s+for\s+"
    r"(?:the\s+|our\s+)?(?P<topic>.+)$",
    re.IGNORECASE,
)
_CONNECTOR_TAIL_RE = re.compile(
    r"(?:\s+(?:will\s+be\s+held|will\s+take\s+place|takes?\s+place|"
    r"is\s+scheduled(?:\s+for)?|is\s+now|is|are|was|were|starts?|will\s+start|"
    r"due(?:\s+on|\s+by)?|deadline\s+is|by|before|on|at|from|till|until|"
    r"for|to))+\s*$",
    re.IGNORECASE,
)


def _strip_title_prefixes(text: str) -> str:
    for _ in range(3):
        before = text
        text = re.sub(
            r"^(?:reminder|update|notice|urgent|important|note)\s*:\s*",
            "", text, flags=re.IGNORECASE,
        )
        text = re.sub(
            r"^(?:dear|hello|hi|hey)\b[^,]{0,30},\s*", "", text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"^(?:all\s+)?students\s+are\s+(?:hereby\s+)?(?:informed|requested|"
            r"advised|reminded)\s+(?:to|that)\s+",
            "", text, flags=re.IGNORECASE,
        )
        text = re.sub(r"^(?:please|kindly)\s+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^don't forget to\s+", "", text, flags=re.IGNORECASE)
        text = text.strip()
        if text == before:
            break
    return text


def _prepared_sentences(text: str) -> list[str]:
    """Sentences with "Reminder:", "Dear students," and "Please" removed."""
    prepared = (_strip_title_prefixes(s) for s in _split_sentences(text))
    return [s for s in prepared if s]


def _pick_sentence(sentences: list[str]) -> str:
    """The first sentence that talks about a task or an event."""
    for sentence in sentences:
        lowered = sentence.lower()
        if _has_task_signal(lowered) or _EVENT_KEYWORD_RE.search(lowered):
            return sentence
    return sentences[0]


def _schedule_spans(sentence: str) -> list[tuple[int, int]]:
    """Where the sentence talks about WHEN (dates, times, relative words)."""
    reference = datetime.now().date()
    spans = [(s, e) for s, e, _ in _absolute_dates(sentence, reference)]
    spans += [(s, e) for s, e, _ in _relative_dates(sentence, reference)]
    spans += [(s, e) for s, e, _ in _time_matches(sentence)]
    spans += [m.span() for m in _VAGUE_PERIOD_RE.finditer(sentence)]
    spans += [m.span() for m in re.finditer(r"\b(?:soon|shortly)\b", sentence, re.I)]
    return sorted(spans)


def _cut_schedule(sentence: str) -> str:
    """Remove the "when" part of a sentence and the words that introduced it."""
    spans = _schedule_spans(sentence)
    if not spans:
        return _CONNECTOR_TAIL_RE.sub("", sentence).strip(" ,;:")

    cut = _CONNECTOR_TAIL_RE.sub("", sentence[:spans[0][0]]).strip(" ,;:")
    if len(cut) >= 3:
        return cut

    # The sentence starts with the date ("Tomorrow at 9 AM: DBMS quiz"):
    # delete the date/time words and keep the rest.
    rest = sentence
    for start, end in reversed(spans):
        rest = rest[:start] + " " + rest[end:]
    rest = re.sub(r"^(?:\s|[,;:\-])+", "", rest)
    rest = re.sub(r"^(?:on|at|by)\s+", "", rest, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", rest).strip(" ,;:")


def _clean_title(text: str) -> str:
    text = re.sub(
        r"\b(submit|finish|complete|prepare|upload|bring)\s+"
        r"(?:the|your|our|a|an)\s+",
        r"\1 ", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"^(?:the|our|a|an|your)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"^(?:can|could|will|would)\s+(?:everyone|all|you|anyone)\s+"
        r"(?:please\s+)?attend\s+",
        "", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"^attend\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(?:the|our|a|an|your)\s+", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip(" .,!?:;")


def _assignment_label(sentence: str) -> str:
    """"Assignment 2" when the message gives a number, otherwise "assignment"."""
    match = re.search(r"\bassignment(?:\s+\d+)?\b", sentence, re.IGNORECASE)
    if match and re.search(r"\d", match.group(0)):
        return match.group(0)
    return "assignment"


def extract_task_title(
    text: str,
    is_event: bool = False,
) -> str | None:
    """Extract a concise task or event title."""
    original = text.strip()
    if not original:
        return None

    subject = extract_subject(original)
    sentences = _prepared_sentences(original)
    if not sentences:
        return None

    sentence = _pick_sentence(sentences).strip(" .,!?:;")
    lower = sentence.lower()

    # Assignments: "Submit <subject> Assignment 2".
    if re.search(r"\bassignment\b", lower):
        action_match = re.search(r"\b(submit|finish|complete)\b", lower)
        label = _assignment_label(sentence)
        if action_match:
            action = action_match.group(1).capitalize()
            return f"{action} {subject} {label}" if subject else f"{action} {label}"
        if re.search(
            r"\bassignment(?:\s+\d+)?\s+(?:is\s+)?due\b"
            r"|\bassignment(?:\s+\d+)?\s+deadline\s+is\b",
            lower,
        ):
            return f"Submit {subject} {label}" if subject else f"Submit {label}"

    # A change notice: "<thing> rescheduled" / "<thing> deadline change".
    change_match = _CHANGE_VERB_RE.search(sentence)
    if change_match and not _EXPLICIT_ACTION_RE.match(lower):
        base = sentence[:change_match.start()]
        base = re.split(r"\boriginally\b", base, flags=re.IGNORECASE)[0]
        base = re.sub(
            r"(?:\s+(?:has|have|had|is|are|was|were|been|now|also|just|be|will|got))+\s*$",
            "", base, flags=re.IGNORECASE,
        )
        base = _clean_title(base)
        deadline_for = re.match(r"deadline for (?P<what>.+)$", base, re.IGNORECASE)
        if deadline_for:
            base = f"{deadline_for.group('what')} deadline"
        if base and subject and subject.lower() not in base.lower():
            # "Project deadline moved ... for Smart Campus": put the subject in front.
            first_word = base.split()[0]
            if first_word[1:].islower():
                base = first_word[0].lower() + base[1:]
            base = f"{subject} {base}"
        if base:
            if re.search(r"\bdeadline$", base, re.IGNORECASE):
                return _capitalise(f"{base} change")
            return _capitalise(f"{base} {change_match.group(1).lower()}")

    # A project proposal that must be uploaded.
    if (
        subject
        and re.search(r"\bproject proposal\b", lower)
        and re.search(r"\b(upload|uploaded)\b", lower)
    ):
        return f"Upload {subject} project proposal"

    # Everything else: drop the "when" part and tidy the rest.
    core = _cut_schedule(sentence)

    # Keep the first clause only: "Workshop, it is already confirmed" -> "Workshop".
    first_clause = re.split(r",\s+", core, maxsplit=1)[0]
    if len(first_clause) >= 3:
        core = first_clause

    passive = _PASSIVE_TITLE_RE.match(core)
    if passive:
        verb = _PASSIVE_VERBS[passive.group("pp").lower()]
        obj = _clean_title(passive.group("obj"))
        return _capitalise(f"{verb} {obj}") if obj else None

    meeting = _MEETING_TITLE_RE.match(core)
    if meeting:
        topic = meeting.group("topic").strip()
        return _capitalise(f"{topic} {meeting.group('kind').lower()} meeting")

    title = _clean_title(core)
    return _capitalise(title) if title else None


# --------------------------------------------------
# DESCRIPTION
# --------------------------------------------------

_PLATFORMS = {
    "moodle": "Moodle",
    "lms": "LMS",
    "google classroom": "Google Classroom",
    "microsoft teams": "Microsoft Teams",
    "ms teams": "MS Teams",
    "teams": "Teams",
    "student portal": "the student portal",
    "portal": "the portal",
    "email": "email",
    "whatsapp": "WhatsApp",
}
_PLATFORM_RE = re.compile(
    r"\b(?:on|via|through|using|in)\s+(?:the\s+)?"
    r"(moodle|lms|google classroom|microsoft teams|ms teams|teams|"
    r"student portal|portal|email|whatsapp)\b",
    re.IGNORECASE,
)
_LOCATION_RE = re.compile(
    r"\b(?:in|at)\s+((?:lab|room|hall|block|classroom)\s+[A-Za-z0-9-]*\d[A-Za-z0-9-]*"
    r"|(?:the\s+)?(?:seminar hall|auditorium))\b",
    re.IGNORECASE,
)


_GREETING_RE = re.compile(
    r"^(?:hi|hello|hey|dear|good\s+(?:morning|afternoon|evening))\b[\w\s,]{0,30}[.!]?$",
    re.IGNORECASE,
)


def extract_description(text: str) -> str | None:
    """Notes about HOW or WHERE: the submission platform, the room, and any
    extra sentences. None when the message has none of these."""
    sentences = _prepared_sentences(text)
    if not sentences:
        return None

    main = _pick_sentence(sentences)
    parts = []

    platform = _PLATFORM_RE.search(text)
    if platform:
        name = _PLATFORMS[platform.group(1).lower()]
        if re.search(r"\b(?:submit|upload)\b", main, re.IGNORECASE):
            parts.append(f"Submit on {name}.")
        else:
            parts.append(f"On {name}.")

    location = _LOCATION_RE.search(text)
    if location:
        parts.append(f"Location: {_capitalise(location.group(1).strip())}.")

    today = datetime.now().date()
    for sentence in sentences:
        if sentence == main or _GREETING_RE.match(sentence):
            continue
        if _absolute_dates(sentence, today) or _time_matches(sentence):
            continue  # the date/time is already captured in its own fields
        parts.append(sentence)

    description = ". ".join(
        part.strip().rstrip(".") for part in parts if part.strip().rstrip(".")
    )
    return description[:300] if description else None


# --------------------------------------------------
# CONFIDENCE
# --------------------------------------------------

def calculate_confidence(
    task_title: str | None,
    task_type: str | None,
    due_date: str | None,
    due_time: str | None,
) -> float:
    """Baseline extraction confidence: 0.25 for each core fact found.

    The four facts are: a title, a type, a date and a time. For an event the
    caller passes the event's date and time as due_date and due_time, so a
    complete event (title, type, date and time) scores 1.0.
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


# --------------------------------------------------
# NOTICE AND POSTER TEXT (roadmap Step 40)
# --------------------------------------------------
# Notices, circulars and posters (typed or read by OCR) have no "please do X"
# sentence. They announce a talk, a distribution or a last date. Rules that
# depend on layout (headlines, several dates, the first time) apply only to
# multi-line text, so a one-line chat message is parsed exactly as before.

_WEEKDAY_NAMES = r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
_SMALL_WORDS = {"a", "an", "the", "of", "for", "in", "on", "at", "to", "and", "or", "by", "with"}


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _is_layout_text(text: str) -> bool:
    """Multi-line text such as a notice or poster (3 or more non-empty lines)."""
    return len(_lines(text)) >= 3


# Buttons and sign-up prompts are not tasks: "Register Now", "Scan the QR code
# to register". Past mentions are not announcements: "Meeting held on 5 August".
_CTA_RE = re.compile(
    r"\b(?:register|apply|enrol+|rsvp)\s+(?:now|here|today)\b"
    r"|\bscan\b[\s\S]{0,40}?\bto\s+(?:register|apply|join)\b",
    re.IGNORECASE,
)
_PAST_MENTION_RE = re.compile(
    r"\b(?:meeting|exam|examination|class|lecture|quiz|viva|workshop|seminar)\s+"
    r"(?:was\s+|were\s+)?held\s+(?:on|in|at)\b",
    re.IGNORECASE,
)
# A platform name on a poster ("Microsoft ... Teams" may be split by OCR).
_PLATFORM_EVENT_RE = re.compile(
    r"\bmicrosoft(?:\W+\w+){0,3}?\W+teams\b|\bms\s+teams\b|\bzoom\b|\bwebex\b"
    r"|\bgoogle\s+meet\b",
    re.IGNORECASE,
)


def _signal_text(text: str, layout: bool) -> str:
    """The text used to decide task / event / notice. For multi-line text the
    sign-up buttons and past mentions are removed first."""
    if not layout:
        return text
    return _PAST_MENTION_RE.sub(" ", _CTA_RE.sub(" ", text))


def _has_schedule(text: str) -> bool:
    today = datetime.now().date()
    return bool(
        _absolute_dates(text, today) or _time_matches(text) or _relative_dates(text, today)
    )


def _scheduled_event_word(text: str) -> bool:
    return bool(_SCHEDULED_EVENT_RE.search(text.lower())) and _has_schedule(text)


def _is_platform_session(signal: str, text: str) -> bool:
    """A scheduled online session whose title word was lost by the OCR."""
    return bool(_PLATFORM_EVENT_RE.search(signal)) and _has_schedule(text)


# "Last date for payment: 4 November", "before 15 November": a labelled deadline.
_DEADLINE_LABEL_RE = re.compile(
    r"\b(?:last\s+date(?:\s+(?:to|for|of)\s+[a-z ]{1,25}?\b)?|due\s+date|deadline|"
    r"(?:on\s+or\s+)?before|no\s+later\s+than)\s*[:\-–]?\s*",
    re.IGNORECASE,
)
_LABEL_GAP_RE = re.compile(
    rf"^(?:(?:the|on)\s+)?(?:{_WEEKDAY_NAMES},?\s*)?$", re.IGNORECASE
)


def _find_deadline_date(text: str, ref: date):
    """(YYYY-MM-DD, start, end) of the date written right after a deadline
    label, or None. The label must be followed by the date itself (only "the",
    "on" or a weekday may sit in between), so a far-away date is never used."""
    dates = _absolute_dates(text, ref)
    best = None
    for label in _DEADLINE_LABEL_RE.finditer(text):
        for start, end, found in dates:
            if start < label.end():
                continue
            if _LABEL_GAP_RE.match(text[label.end():start].strip()):
                best = (found.isoformat(), start, end)
            break
    return best


def _within_one_edit(a: str, b: str) -> bool:
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    return any(long_[:i] + long_[i + 1:] == short for i in range(len(long_)))


def _context_fix(phrase: str, text: str) -> str:
    """Fix an obvious OCR slip in a headline using the rest of the text: a word
    that appears once, with a word one letter away on ANOTHER line ("Nert" in
    the headline, "your next semester" in the body), becomes that word. Nothing
    is changed when the text offers no such word. Used once per title."""
    lines = [line.lower() for line in text.splitlines()]
    total = {}
    for token in re.findall(r"[a-z]{4,}", text.lower()):
        total[token] = total.get(token, 0) + 1

    fixed = []
    for word in phrase.split():
        core = word.strip(".,:;!?()")
        lower = core.lower()
        if core.isalpha() and len(core) >= 4 and total.get(lower) == 1:
            body = {}
            for line in lines:
                if re.search(rf"\b{lower}\b", line):
                    continue
                for token in re.findall(r"[a-z]{4,}", line):
                    body[token] = body.get(token, 0) + 1
            near = sorted(
                (t for t in body if _within_one_edit(t, lower)), key=lambda t: -body[t]
            )
            if near and (len(near) == 1 or body[near[0]] > body[near[1]]):
                replacement = near[0].capitalize() if core[0].isupper() else near[0]
                word = word.replace(core, replacement)
        fixed.append(word)
    return " ".join(fixed)


def _title_case_caps(text: str) -> str:
    """ALL-CAPS poster text becomes Title Case; mixed-case words are kept."""
    letters = [c for c in text if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) / len(letters) < 0.6:
        return text
    words = []
    for index, word in enumerate(text.split()):
        if word.isupper() and any(c.isalpha() for c in word):
            word = word.title() if index == 0 or word.lower() not in _SMALL_WORDS else word.lower()
        words.append(word)
    return " ".join(words)


_ANNOUNCE_RE = re.compile(
    r"^(?:notice|circular)(?:\s*[:\-–]\s*(?P<rest>.+)|\s*)$", re.IGNORECASE
)
_ALERT_RE = re.compile(r"^(?P<kind>session|event|webinar|workshop|seminar)\s+alert$", re.IGNORECASE)
_DEBATE_RE = re.compile(r"^debate\s+topic\s*:?\s*(?P<rest>.*)$", re.IGNORECASE)
_KIND_ON_RE = re.compile(
    r"^(?:an?\s+)?(?P<kind>(?:invited\s+|guest\s+|expert\s+)?"
    r"(?:talk|webinar|session|seminar|workshop|lecture))\s+on\b\s*(?P<rest>.*)$",
    re.IGNORECASE,
)
_APPLICATIONS_RE = re.compile(r"\bapplications?\s+(?:are\s+)?(?:live|open)", re.IGNORECASE)
_STOP_LINE_RE = re.compile(
    r"^(?:by\b|dr\.?\s|prof\.?\s|mr\.?\s|mrs\.?\s|ms\.?\s|associate\b|assistant\b|"
    r"scan\b|register\b)",
    re.IGNORECASE,
)
_LABEL_LINE_RE = re.compile(r"^[A-Za-z][A-Za-z ]{0,15}:$")


def _ends_block(line: str) -> bool:
    today = datetime.now().date()
    return bool(
        _STOP_LINE_RE.match(line)
        or _LABEL_LINE_RE.match(line)
        or _time_matches(line)
        or _absolute_dates(line, today)
    )


def _is_junk_line(line: str) -> bool:
    """A lone short word (OCR noise such as "Gen"); "&" and small words stay."""
    return bool(re.fullmatch(r"[A-Za-z]{1,4}", line)) and line.lower() not in _SMALL_WORDS


def _following_lines(lines: list[str], start: int, limit: int) -> list[str]:
    taken = []
    for line in lines[start:]:
        if _ends_block(line):
            break
        if _is_junk_line(line):
            continue
        taken.append(line)
        if len(taken) >= limit:
            break
    return taken


def _headline_after_notice(lines: list[str], index: int) -> str | None:
    """The line after a bare "NOTICE", joined with the next one when it ends
    in a connector ("Grade Card Distribution for" + "Semester")."""
    following = _following_lines(lines, index + 1, 3)
    if not following:
        return None
    headline = following[0]
    for extra in following[1:]:
        if headline.split()[-1].lower() in _SMALL_WORDS:
            headline = f"{headline} {extra}"
        else:
            break
    return headline if len(headline.split()) <= 10 else None


def _layout_title(text: str) -> str | None:
    """A title taken from the headline of a notice or poster, or None."""
    lines = _lines(text)
    title = None
    payment_title = False

    for index, line in enumerate(lines):
        alert = _ALERT_RE.match(line)
        debate = _DEBATE_RE.match(line)
        if alert:
            name = " ".join(_following_lines(lines, index + 1, 4))
            title = f"{name} {alert['kind'].lower()}" if name else None
        elif debate:
            topic = debate["rest"].strip() or " ".join(_following_lines(lines, index + 1, 3))
            title = f"Debate: {topic}" if topic else None
        if title:
            break

    if not title:
        for index, line in enumerate(lines):
            announce = _ANNOUNCE_RE.match(line)
            if not announce:
                continue
            headline = (announce["rest"] or "").strip() or _headline_after_notice(lines, index)
            if not headline:
                continue
            payment = re.match(r"payment of\s+(.+)$", headline, re.IGNORECASE)
            if payment:
                title = "Pay " + payment.group(1)
                payment_title = True
            else:
                title = headline
            break

    if not title:
        for index, line in enumerate(lines):
            match = _KIND_ON_RE.match(line)
            if not match:
                continue
            rest = match["rest"].strip()
            topic = rest if rest else " ".join(_following_lines(lines, index + 1, 4))
            if topic and not _has_schedule(topic) and len(topic.split()) <= 14:
                title = f"{match['kind'].capitalize()} on {_title_case_caps(topic)}"
                break

    if not title:
        for index, line in enumerate(lines):
            if not _APPLICATIONS_RE.search(line):
                continue
            before = line[:_APPLICATIONS_RE.search(line).start()].strip()
            parts = [before] if before else []
            for earlier in reversed(lines[max(0, index - 2):index]):
                if earlier.upper() == earlier and any(c.isalpha() for c in earlier):
                    parts.insert(0, earlier)
                else:
                    break
            if parts:
                title = "Apply for " + _title_case_caps(" ".join(parts))
                break

    if not title:
        # A poster headline written as a question: "The Future of Work:" / "Are You Ready?"
        for index, line in enumerate(lines):
            if line.endswith("?") and sum(len(re.sub(r"\W", "", w)) >= 3 for w in line.split()) >= 3:
                previous = lines[index - 1] if index else ""
                title = f"{previous} {line}" if previous.endswith(":") else line
                break

    if not title:
        return None
    title = re.sub(r"\s+", " ", title).strip(" .,:;")
    title = _context_fix(title, text)
    if payment_title:  # "Pay Next Semester Fees" -> "Pay next semester fees"
        words = title.split()
        title = " ".join(words[:1] + [w.lower() if w.istitle() else w for w in words[1:]])
    return _capitalise(title) if title else None


_LAYOUT_PLATFORMS = (
    ("microsoft", "Microsoft Teams"), ("ms teams", "MS Teams"), ("zoom", "Zoom"),
    ("webex", "Webex"), ("google", "Google Meet"),
)


def _date_literal(text: str, start: int, end: int) -> str:
    """The date as written, with the weekday in front of it when there is one."""
    weekday = re.search(rf"{_WEEKDAY_NAMES},?\s*$", text[:start], re.IGNORECASE)
    literal = text[weekday.start():end] if weekday else text[start:end]
    return _tidy(re.sub(r"\s+,", ",", re.sub(r"\s+", " ", literal)))


def _layout_description(text: str, listed_dates: list) -> str | None:
    """Useful notes for a notice or poster: every date when no single one can
    be chosen, a date range, the platform, the mode and the venue. OCR noise
    lines are not copied."""
    parts = []

    if listed_dates:
        literals = [_date_literal(text, s, e) for s, e, _ in listed_dates]
        parts.append("Dates: " + "; ".join(literals) + ".")
    else:
        date_range = _DAY_RANGE_RE.search(text)
        if date_range and not _CHANGE_VERB_RE.search(text[max(0, date_range.start() - 60):date_range.start()]):
            parts.append(f"Dates: {_tidy(date_range.group(0))}.")

    platform = _PLATFORM_EVENT_RE.search(text)
    if platform:
        lowered = platform.group(0).lower()
        name = next(label for key, label in _LAYOUT_PLATFORMS if lowered.startswith(key))
        parts.append(f"Platform: {name}.")

    mode = re.search(r"\bmode\s*:\s*(online|offline|hybrid)\b", text, re.IGNORECASE)
    if mode:
        parts.append(f"Mode: {mode.group(1).capitalize()}.")

    location = _LOCATION_RE.search(text)
    venue = re.search(r"\bvenue\s*:\s*\n?\s*([^\n]{3,60})", text, re.IGNORECASE)
    if location:
        parts.append(f"Location: {_capitalise(location.group(1).strip())}.")
    elif venue:
        parts.append(f"Location: {venue.group(1).strip(' .')}.")

    return " ".join(parts)[:300] if parts else None


# --------------------------------------------------
# MAIN PARSER
# --------------------------------------------------

_UNKNOWN_DEADLINE_RE = re.compile(
    r"(deadline|due date).{0,50}"
    r"(not been announced|not announced|unknown|will be announced|"
    r"has not been announced|to be announced|tba|tbd|not yet decided|"
    r"not decided|will be communicated|will be informed)"
)


def _empty_result(raw_text: str, source: str) -> dict:
    """The contract-shaped result when nothing task-like was found."""
    return {
        "task_title": None,
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
        "change_information": [],
    }


def _parse(raw_text, source, reference_date):
    """Return (result, category); category is task, event or general_notice."""
    if raw_text is None:
        raw_text = ""
    elif not isinstance(raw_text, str):
        raw_text = str(raw_text)

    result = _empty_result(raw_text, source)
    text = nlp(raw_text).text.strip()
    if not text:
        return result, "general_notice"

    ref = _as_date(reference_date)
    text_lower = text.lower()

    # Multi-line text (a notice or poster) is read with a few extra rules.
    layout = _is_layout_text(text)
    signal = _signal_text(text, layout)  # the text itself for ordinary messages
    signal_lower = signal.lower()
    changed = bool(_CHANGE_VERB_RE.search(text))

    if is_general_notice(signal):
        return result, "general_notice"

    event = is_event_message(signal)
    if layout and not event and not _has_task_signal(signal_lower):
        event = _is_platform_session(signal, text)

    # "Last date for payment: 4 November" makes a task, whatever else is said.
    deadline_hit = None if changed else _find_deadline_date(text, ref)
    if deadline_hit:
        event = False

    if not (event or deadline_hit or _has_task_signal(signal_lower)):
        return result, "general_notice"

    title = _layout_title(text) if layout else None
    task_type = classify_task_type(title or text)
    if event and re.search(
        r"\b(?:seminar|workshop|cultural fest|college fest|festival)\b",
        text_lower,
    ):
        task_type = "event"
    if event and task_type is None:
        task_type = "event"

    date_hit = deadline_hit or _find_date(text, ref)
    time_hit = _find_time(text, first=layout and not changed)

    # Several separate dates and no label saying which one counts: choose none
    # (they are kept in the description).
    listed_dates = []
    if layout and not changed and not deadline_hit:
        explicit = _absolute_dates(text, ref)
        if len({found for _, _, found in explicit}) >= 2:
            date_hit = None
            listed_dates = explicit

    # A deadline described as unknown must not be inferred.
    if _UNKNOWN_DEADLINE_RE.search(text_lower):
        date_hit = time_hit = None
        listed_dates = []

    found_date = date_hit[0] if date_hit else None
    found_time = time_hit[0] if time_hit else None

    due_date, due_time, event_datetime = found_date, found_time, None
    if event:
        # An event keeps its date and time together; with only one of them
        # event_datetime stays None (the literal words are still kept in
        # date_time_expression).
        if found_date and found_time:
            event_datetime = f"{found_date}T{found_time}:00"
        due_date = None
        due_time = None

    if title is None:
        title = extract_task_title(signal if layout else text, is_event=event)

    result.update({
        "task_title": title,
        "description": (
            _layout_description(text, listed_dates) if layout else extract_description(text)
        ),
        "task_type": task_type,
        "subject": extract_subject(text),
        "due_date": due_date,
        "due_time": due_time,
        "event_datetime": event_datetime,
        "date_time_expression": _build_expression(text, date_hit, time_hit),
        "confidence": calculate_confidence(title, task_type, found_date, found_time),
    })
    return result, ("event" if event else "task")


def parse_message(
    raw_text: str,
    source: str,
    reference_date: datetime | date | None = None,
) -> dict:
    """Convert a message into structured task/event fields."""
    return _parse(raw_text, source, reference_date)[0]


def classify_message_category(
    raw_text: str,
    reference_date: datetime | date | None = None,
) -> str:
    """Return "task", "event" or "general_notice" for a message."""
    return _parse(raw_text, "", reference_date)[1]
