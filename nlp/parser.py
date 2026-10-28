

import re

import spacy

from datetime import datetime, timedelta





nlp = spacy.blank("en")





# --------------------------------------------------

# SUBJECT EXTRACTION

# --------------------------------------------------



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

]





def extract_subject(text: str) -> str | None:

    """Extract a recognized academic subject."""



    for subject in sorted(SUBJECTS, key=len, reverse=True):

        match = re.search(

            rf"(?<!\w){re.escape(subject)}(?!\w)",

            text,

            re.IGNORECASE,

        )



        if match:

            return subject



    return None





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

# MESSAGE CATEGORY

# --------------------------------------------------



def is_general_notice(text: str) -> bool:

    """

    Identify announcements that should not become tasks or events.

    """



    text_lower = text.lower()



    if re.search(

        r"\b(exam timetable|timetable has been published)\b",

        text_lower,

    ):

        return True



    if re.search(

        r"\blibrary will remain closed\b",

        text_lower,

    ):

        return True



    if (

        "semester registration opens" in text_lower

        and not re.search(

            r"\b(complete|submit|register by|deadline)\b",

            text_lower,

        )

    ):

        return True



    return False





def is_event_message(text: str) -> bool:

    """

    Identify scheduled events, rather than tasks with deadlines.

    """



    text_lower = text.lower()



    event_patterns = [

        r"\bmeeting\b",

        r"\bseminar\b",

        r"\bworkshop\b",

        r"\blecture\b",

        r"\bviva\b",

        r"\bcultural fest\b",

        r"\bcollege fest\b",

        r"\bfestival\b",

        r"\bquiz\b",

        r"\bexam\b",

        r"\bexamination\b",

    ]



    has_event_keyword = any(

        re.search(pattern, text_lower)

        for pattern in event_patterns

    )



    if not has_event_keyword:

        return False



    # An explicit task action and a deadline generally indicate

    # a task, even when the task is called a quiz or exam.

    has_task_action = bool(

        re.search(

            r"\b(submit|complete|finish|upload|prepare|"

            r"study|revise|solve|read)\b",

            text_lower,

        )

    )



    if has_task_action:

        return False



    return True





# --------------------------------------------------

# DATE EXTRACTION

# --------------------------------------------------



def extract_date(

    text: str,

    reference_date: datetime | None = None,

) -> str | None:

    """Extract explicit and relative dates."""



    if reference_date is None:

        reference_date = datetime.now()



    text_lower = text.lower()



    if re.search(r"\bnext week\b", text_lower):

        return None



    if re.search(r"\btomorrow\b", text_lower):

        return (

            reference_date + timedelta(days=1)

        ).strftime("%Y-%m-%d")



    if re.search(r"\btoday\b", text_lower):

        return reference_date.strftime("%Y-%m-%d")



    current_year = reference_date.year



    patterns = [

        (

            r"\b\d{4}-\d{1,2}-\d{1,2}\b",

            "iso",

        ),

        (

            r"\b\d{1,2}(?:st|nd|rd|th)?\s+"

            r"(January|February|March|April|May|June|July|"

            r"August|September|October|November|December)\b",

            "day_month",

        ),

        (

            r"\b(January|February|March|April|May|June|July|"

            r"August|September|October|November|December)\s+"

            r"\d{1,2}(?:st|nd|rd|th)?\b",

            "month_day",

        ),

    ]



    found_dates = []



    for pattern, date_format in patterns:

        for match in re.finditer(

            pattern,

            text,

            re.IGNORECASE,

        ):

            try:

                value = match.group(0)



                if date_format == "iso":

                    parsed = datetime.strptime(

                        value,

                        "%Y-%m-%d",

                    )



                elif date_format == "day_month":

                    cleaned = re.sub(

                        r"(st|nd|rd|th)\b",

                        "",

                        value,

                        flags=re.IGNORECASE,

                    )



                    parsed = datetime.strptime(

                        f"{cleaned} {current_year}",

                        "%d %B %Y",

                    )



                else:

                    cleaned = re.sub(

                        r"(st|nd|rd|th)\b",

                        "",

                        value,

                        flags=re.IGNORECASE,

                    )



                    parsed = datetime.strptime(

                        f"{cleaned} {current_year}",

                        "%B %d %Y",

                    )



                found_dates.append(

                    (match.start(), parsed)

                )



            except ValueError:

                continue



    if found_dates:

        # Prefer the last date mentioned. This helps with

        # messages that state an old date followed by a new date.

        _, selected_date = max(

            found_dates,

            key=lambda item: item[0],

        )



        return selected_date.strftime("%Y-%m-%d")



    weekdays = {

        "monday": 0,

        "tuesday": 1,

        "wednesday": 2,

        "thursday": 3,

        "friday": 4,

        "saturday": 5,

        "sunday": 6,

    }



    weekday_matches = list(

        re.finditer(

            r"\b(next\s+)?"

            r"(monday|tuesday|wednesday|thursday|"

            r"friday|saturday|sunday)\b",

            text_lower,

        )

    )



    if weekday_matches:

        match = weekday_matches[-1]

        weekday = match.group(2)



        days_ahead = (

            weekdays[weekday] - reference_date.weekday()

        ) % 7



        if days_ahead == 0:

            days_ahead = 7



        return (

            reference_date + timedelta(days=days_ahead)

        ).strftime("%Y-%m-%d")



    return None





# --------------------------------------------------

# TIME EXTRACTION

# --------------------------------------------------



def extract_time(text: str) -> str | None:

    """Extract a time and normalize it to HH:MM."""



    patterns = [
        r"(?<!\d)(\d{1,2}):(\d{2})\s*(AM|PM)\b",
        r"(?<![\d:])(\d{1,2})\s*(AM|PM)\b",
        r"(?<![\d-])([01]?\d|2[0-3]):([0-5]\d)(?!\s*(?:AM|PM)\b)",
    ]

    matches_found = []



    for priority, pattern in enumerate(patterns):

        for match in re.finditer(

            pattern,

            text,

            re.IGNORECASE,

        ):

            matches_found.append(

                (match.start(), priority, match)

            )



    if not matches_found:

        return None



    # Select the last time mentioned in the message.

    _, priority, match = max(

        matches_found,

        key=lambda item: item[0],

    )



    try:

        if priority == 0:

            hour = int(match.group(1))

            minute = int(match.group(2))

            period = match.group(3).upper()



        elif priority == 1:

            hour = int(match.group(1))

            minute = 0

            period = match.group(2).upper()



        else:

            hour = int(match.group(1))

            minute = int(match.group(2))

            period = None



        if period == "PM" and hour != 12:

            hour += 12

        elif period == "AM" and hour == 12:

            hour = 0



        if hour > 23 or minute > 59:

            return None



        return f"{hour:02d}:{minute:02d}"



    except ValueError:

        return None





# --------------------------------------------------

# TASK TITLE EXTRACTION

# --------------------------------------------------



def extract_task_title(
    text: str,
    is_event: bool = False,
) -> str | None:
    """Extract a concise task or event title."""

    original = text.strip()
    if not original:
        return None

    title = re.sub(
        r"^(?:reminder|update|notice)\s*:\s*",
        "",
        original,
        flags=re.IGNORECASE,
    ).strip()
    title = re.sub(r"^(?:please\s+|kindly\s+)?", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"^don't forget to\s+", "", title, flags=re.IGNORECASE).strip()

    lower = original.lower()
    subject = extract_subject(original)

    # Standardize common task titles before generic cleanup.
    if re.search(r"\bbring\s+(?:your\s+)?id card\b", lower):
        return "Bring ID card to campus"

    # Assignment titles retain the capitalization and number in the source.
    if re.search(r"\bassignment\b", lower):
        action_match = re.search(r"\b(submit|finish|complete)\b", lower)
        if action_match:
            action = action_match.group(1).capitalize()
            assignment_match = re.search(
                r"\bassignment(?:\s+\d+)?\b",
                original,
                re.IGNORECASE,
            )
            assignment_label = (assignment_match.group(0) if assignment_match and re.search(r"\d", assignment_match.group(0)) else "assignment")
            if subject:
                return f"{action} {subject} {assignment_label}"
            return f"{action} {assignment_label}"

        if re.search(r"\bassignment\s+(?:is\s+)?due\b|\bassignment deadline is\b", lower):
            if subject:
                return f"Submit {subject} assignment"
            return "Submit assignment"

        if re.search(r"\bsubmit\s+(?:your\s+)?assignment\b", lower):
            return "Submit assignment"

    # Preserve rescheduling/change intent in titles.
    if subject and re.search(r"\bquiz\b", lower) and re.search(r"\b(rescheduled|postponed|moved)\b", lower):
        return f"{subject} quiz rescheduled"

    if subject and re.search(r"\bquiz\b", lower):
        action_match = re.search(r"\b(complete|finish|submit)\b", lower)
        if action_match:
            return f"{action_match.group(1).capitalize()} {subject} quiz"

    if subject and re.search(r"\bproject\s+deadline\b", lower) and re.search(r"\b(change|changed|moved|extended|postponed)\b", lower):
        return f"{subject} project deadline change"

    # Canonicalize common meeting phrasing.
    if re.search(r"\bteam meeting\b", lower) and re.search(r"\bfinal-year project\b", lower):
        return "Final-year project team meeting"
    if re.search(r"\bproject review meeting\b", lower):
        return "Project review meeting"

    # Messages without action verbs can still describe a task.
    if subject and re.search(r"\bassignment\s+(?:is\s+)?due\b|\bassignment deadline is\b", lower):
        return f"Submit {subject} assignment"
    if subject and re.search(r"\bproject proposal\b", lower) and re.search(r"\b(upload|uploaded)\b", lower):
        return f"Upload {subject} project proposal"

    # Keep only the first sentence.
    title = re.split(r"\.\s+|;\s+", title, maxsplit=1)[0].strip()

    # Remove dates, times, and scheduling clauses at the end.
    title = re.sub(
        r"\s+(?:"
        r"originally planned for|rescheduled to|postponed to|moved from|moved to|"
        r"changed to|will be held|will take place|is scheduled for|starts|"
        r"deadline has moved|deadline is|is due|due on|due by|by|before|on|at"
        r")\s+.+$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    title = re.sub(
        r"\s+(?:today|tomorrow|tonight|soon|next\s+(?:monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday|week))$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    title = re.sub(
        r"\s+(?:will be held|is scheduled|starts|will take place|is on|is now|is)$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    title = re.sub(
        r"\b(submit|finish|complete|prepare|upload|bring)\s+(?:the|your|our|a|an)\s+",
        r"\1 ",
        title,
        flags=re.IGNORECASE,
    )

    title = re.sub(r"^(?:the|our|a|an|your)\s+", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"^can everyone attend\s+", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"^attend\s+", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"^(?:the|our|a|an|your)\s+", "", title, flags=re.IGNORECASE).strip()

    title = re.sub(r"\s+", " ", title).strip(" .,!?:;")
    if not title:
        return None

    return title[0].upper() + title[1:]


def calculate_confidence(

    task_title: str | None,

    task_type: str | None,

    due_date: str | None,

    due_time: str | None,

) -> float:

    """Calculate baseline extraction confidence."""



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

# MAIN PARSER

# --------------------------------------------------



def parse_message(

    raw_text: str,

    source: str,

    reference_date: datetime | None = None,

) -> dict:

    """Convert a message into structured task/event fields."""



    text = nlp(raw_text).text.strip()

    text_lower = text.lower()



    if reference_date is None:

        reference_date = datetime.now()



    if is_general_notice(text):

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

        "read",

        "bring",

    ]



    is_task = any(

        re.search(

            rf"\b{re.escape(word)}\b",

            text_lower,

        )

        for word in action_words

    )



    event = is_event_message(text)



    # Explicit task actions usually indicate tasks rather than events.
    # "Attend" is different: attending a workshop/meeting is still an event.
    explicit_task_action = bool(
        re.search(
            r"(submit|complete|finish|upload|prepare|study|revise|solve|read|bring)",
            text_lower,
        )
    )
    if is_task and explicit_task_action:
        event = False



    task_type = classify_task_type(text)

    subject = extract_subject(text)



    # A general exam timetable announcement is handled above.

    task_title = (

        extract_task_title(text, is_event=event)

        if is_task or event

        or re.search(r"\bassignment deadline is\b", text_lower)

        or re.search(r"\bassignment is due\b", text_lower)

        or re.search(r"\bproject proposal\b", text_lower)
        or (
            re.search(r"\bproject\s+deadline\b", text_lower)
            and re.search(r"\b(change|changed|moved|extended|postponed)\b", text_lower)
        )
        else None

    )



    # For non-task scheduled events, use event-style type classification.

    if event and any(

        word in text_lower

        for word in [

            "seminar",

            "workshop",

            "cultural fest",

            "college fest",

            "festival",

        ]

    ):

        task_type = "event"



    extracted_date = extract_date(text, reference_date)

    extracted_time = extract_time(text)



    due_date = extracted_date

    due_time = extracted_time

    event_datetime = None



    # A deadline described as unknown must not be inferred.

    deadline_unknown = bool(

        re.search(

            r"(deadline|due date).{0,50}"

            r"(not been announced|not announced|unknown|"

            r"will be announced|has not been announced)",

            text_lower,

        )

    )



    if deadline_unknown:

        due_date = None

        due_time = None



    if event:

        if extracted_date and extracted_time:

            event_datetime = (

                f"{extracted_date}T{extracted_time}:00"

            )



        due_date = None

        due_time = None



    confidence = calculate_confidence(

        task_title,

        task_type,

        due_date,

        due_time,

    )



    return {

        "task_title": task_title,

        "description": None,

        "task_type": task_type,

        "subject": subject,

        "due_date": due_date,

        "due_time": due_time,

        "event_datetime": event_datetime,

        "source": source,

        "raw_text": raw_text,

        "date_time_expression": None,

        "confidence": confidence,

        "change_information": [],

    }
