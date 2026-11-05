# NLP Input/Output Interface

## 1. Purpose

This document defines the input and output interface of the NLP/message-understanding module for Phase 1.

The NLP module converts unstructured student messages, notices, or OCR-extracted text into structured task and event information that can be consumed by the task/storage layer and the intelligence layer.

## 2. NLP Input

The NLP module receives the following core inputs:

Example:

    {
      "raw_text": "Please submit your Machine Learning Assignment 1 by 15th October at 5 PM.",
      "source": "LMS Notice"
    }

### Input Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `raw_text` | string | Yes | Unstructured student message, notice, or OCR-extracted text to be processed. |
| `source` | string | Yes | Source channel or platform from which the text originated. |

Possible source values include:

- WhatsApp
- Email
- LMS
- Notice
- Screenshot/OCR
- Manual input
- Other

## 3. NLP Processing Flow

    Raw Text
       |
       v
    Text Cleaning / Normalization
       |
       v
    Task / Event Detection
       |
       v
    Task Title & Description Extraction
       |
       v
    Task / Event Type Classification
       |
       v
    Subject Extraction
       |
       v
    Date Extraction
       |
       v
    Time Extraction
       |
       v
    Date-Time Expression Extraction
       |
       v
    Event Date-Time Extraction
       |
       v
    Change Detection
       |
       v
    Confidence Calculation
       |
       v
    Structured NLP Output

## 4. NLP Output

The NLP module provides the following fields from the shared structured data contract:

Example:

    {
      "task_title": "Submit Machine Learning Assignment 1",
      "description": "Submit on Moodle",
      "task_type": "assignment",
      "subject": "Machine Learning",
      "due_date": "2026-10-15",
      "due_time": "17:00",
      "event_datetime": null,
      "source": "LMS Notice",
      "raw_text": "Please submit your Machine Learning Assignment 1 by 15th October at 5 PM.",
      "date_time_expression": "15th October at 5 PM",
      "confidence": 0.95,
      "change_information": []
    }

### NLP Output Fields

| Field | Type | Description |
|---|---|---|
| `task_title` | string | Extracted task title or action headline. |
| `description` | string / null | Detailed description, instructions, or notes. |
| `task_type` | string | Classified type such as assignment, exam, quiz, project, event, announcement, or notice. |
| `subject` | string / null | Course or subject name/code when available. |
| `due_date` | string / null | Extracted due/submission date in `YYYY-MM-DD` format when sufficient information is available. |
| `due_time` | string / null | Extracted due/submission time in `HH:MM` format when sufficient information is available. |
| `event_datetime` | string / null | Scheduled datetime for an event such as an exam, viva, class, or meeting. |
| `source` | string | Source channel or platform. |
| `raw_text` | string | Original unstructured input text. |
| `date_time_expression` | string / null | Literal date/time expression extracted from the source text. |
| `confidence` | float | NLP extraction confidence between `0.0` and `1.0`. |
| `change_information` | array | Detected changes. Empty array when no change is detected. |

## 5. Fields Not Owned by NLP

The NLP module does not generate or maintain the following fields:

| Field | Owner | Responsibility |
|---|---|---|
| `task_id` | Task/Storage Layer | Unique identifier assigned when the task is stored. |
| `due_datetime` | Task/Storage Layer | Final normalized datetime used by downstream intelligence. |
| `status` | Task/Storage Layer | Authoritative task status. |
| `created_at` | Task/Storage Layer | Timestamp when the task is created. |
| `completed_at` | Task/Storage Layer | Timestamp when the task is marked completed. |

The intelligence layer calculates:

- `priority_score`
- `priority_label`
- `priority_reason`
- workload metrics
- productivity metrics
- risk signals

## 6. Missing Information

NLP must not invent information that is not present or cannot be reliably inferred.

Missing or unknown information must be represented as:

    null

For example:

    {
      "task_title": "Submit the Machine Learning assignment",
      "task_type": "assignment",
      "due_date": null,
      "due_time": null
    }

NLP must not infer a deadline or time merely because one would normally be expected for that task.

NLP must also not infer that a task is completed or overdue from the message itself. Task status is maintained by the task/storage layer.

## 7. Date and Time Handling

NLP should identify both explicit and relative date/time expressions.

Examples include:

- today
- tomorrow
- Monday
- next Monday
- next week
- by Friday
- 15th October
- 5 PM
- tomorrow at 11:59 PM

The original expression should be preserved in:

    {
      "date_time_expression": "tomorrow at 11:59 PM"
    }

Where sufficient information is available, NLP extracts:

- `due_date`
- `due_time`
- `event_datetime`

The task/storage layer is responsible for final validation, normalization of `due_datetime`, and timezone handling before persistence.

## 8. Event Date-Time

`event_datetime` is used for scheduled events such as:

- examinations
- viva
- classes
- meetings
- other scheduled events

It is distinct from a submission deadline.

Example:

    {
      "task_type": "exam",
      "event_datetime": "2026-10-15T10:00:00"
    }

NLP extracts the event date/time from the source text and provides `event_datetime` in ISO 8601 format when sufficient information is available. The task/storage layer validates it and handles final normalization or timezone handling before persistence.

## 9. Change Information

`change_information` is an array because a single message may contain multiple changes.

When no change is detected:

    {
      "change_information": []
    }

When a change is detected:

    {
      "change_information": [
        {
          "is_changed": true,
          "change_type": "deadline",
          "old_value": "Friday 11:59 PM",
          "new_value": "Monday 11:59 PM"
        }
      ]
    }

Each change object contains:

- `is_changed`
- `change_type`
- `old_value`
- `new_value`

Possible `change_type` values include:

- `deadline`
- `date`
- `time`
- `location`
- `other`

Multiple changes can be represented in the same message.

## 10. OCR Compatibility

The NLP module must also accept text produced by the OCR pipeline.

The intended integration is:

    Screenshot
        |
        v
       OCR
        |
        v
    Extracted Text
        |
        v
       NLP
        |
        v
    Structured Output

The NLP module should process OCR-extracted text using the same NLP interface as other text sources.

The `source` field should preserve that the input originated from OCR/screenshot when such metadata is available.

### OCR adapter (Roadmap Step 36)

`nlp/ocr_adapter.py` connects the OCR module's JSON output to `parse_message`. The shared NLP contract is not changed.

Input: one OCR record per screenshot, with these fields:

| Field | Meaning | Required |
|---|---|---|
| `source` | Image file name, e.g. `screenshot 9.jpeg` | yes (non-empty text) |
| `cleaned_text` | Whitespace-normalised OCR text; the only text given to the parser | yes (may be empty) |
| `overall_confidence` | Average OCR confidence from 0 to 1, or `null` if no text was found | key required, value may be `null` |
| `confidence` | List of `{"text": ..., "score": 0-1}`, one per text line | yes (may be an empty list) |
| `raw_text` | Original OCR text; ignored by the adapter | no |

Functions: `parse_ocr_record(record, reference_date=None)` and `parse_ocr_file(path, reference_date=None)`. Both return:

    {
      "task": { ...normal parse_message output, "source" = "Screenshot/OCR"... },
      "ocr":  {
        "image_filename": "screenshot 9.jpeg",
        "overall_confidence": 0.6024,
        "line_confidences": [{"text": "...", "score": 0.65}, ...]
      }
    }

- `reference_date` is passed to `parse_message` unchanged.
- The NLP `confidence` inside `task` measures how many fields were found. The OCR confidence measures how sure the OCR engine was about the text. They are stored in different places and never mixed or used to change each other.
- Empty OCR text is accepted. `task` is then the normal empty "general notice" result, and `ocr` is still returned.
- A missing required field or an invalid value raises `OCRRecordError` (a `ValueError`) whose message names the field.

## 11. Example: Message to Structured Output

### Input

    {
      "raw_text": "Dear Students, please submit your Machine Learning Assignment 1 on Moodle by 15th October at 5:00 PM.",
      "source": "LMS Notice"
    }

### NLP Output

    {
      "task_title": "Submit Machine Learning Assignment 1",
      "description": "Submit on Moodle",
      "task_type": "assignment",
      "subject": "Machine Learning",
      "due_date": "2026-10-15",
      "due_time": "17:00",
      "event_datetime": null,
      "source": "LMS Notice",
      "raw_text": "Dear Students, please submit your Machine Learning Assignment 1 on Moodle by 15th October at 5:00 PM.",
      "date_time_expression": "15th October at 5:00 PM",
      "confidence": 0.95,
      "change_information": []
    }

The task/storage layer subsequently handles:

- `task_id`
- `due_datetime`
- `status`
- `created_at`
- `completed_at`

## 12. Interface Boundary

    NLP MODULE

    Input                                      Output

    raw_text  ------------------+
                                |
    source    ------------------+
                                |
                                v
                           NLP Processing
                                |
                                v
                    +-------------------------+
                    | task_title              |
                    | description             |
                    | task_type               |
                    | subject                 |
                    | due_date                |
                    | due_time                |
                    | event_datetime          |
                    | source                  |
                    | raw_text                |
                    | date_time_expression    |
                    | confidence              |
                    | change_information      |
                    +-------------------------+
                                |
                                v
                        Task / Storage Layer
                                |
                                v
                    task_id / due_datetime /
                    status / timestamps
                                |
                                v
                        Intelligence Layer
                                |
                                v
                    Priority / Workload / Risk

## 13. Interface Responsibility

The NLP module is responsible for extracting and classifying information from unstructured text.

The task/storage layer is responsible for persistence, task identity, authoritative status, timestamps, final datetime normalization, and timezone handling.

The intelligence layer is responsible for priority scoring, workload analysis, productivity analysis, and risk signals.

This interface serves as the contract between the NLP module and the downstream system components.

## 14. Phase 2 Implementation Notes (Roadmap Steps 14-21)

This section records how `nlp/parser.py` applies the interface above. It adds no new output fields.

### Message categories

Every message is treated as one of three categories. The category is not an output field; `classify_message_category()` returns it for testing.

| Category | Meaning | Output |
|---|---|---|
| `task` | The student must do something (submit, complete, bring, register ...) or a deadline is stated. | `due_date` / `due_time`. |
| `event` | Something is scheduled (exam, quiz, viva, class, meeting, seminar, workshop, fest ...) and nothing must be handed in. | `event_datetime`; `due_date` and `due_time` stay `null`. |
| `general_notice` | An announcement (timetable published, closure, registration opens, holiday) or chatter. | Every extracted field is `null`, `confidence` is `0.0`. |

An explicit action word beats an event word, so "Complete the quiz before 7 PM" is a task and "Quiz on Friday at 2 PM" is an event. "Attend" keeps an event an event.

### Dates and times

- An explicit calendar date beats a relative word (`tomorrow`, `today`, `tonight`, a weekday). If several explicit dates appear, the last one wins, so "moved from 8 November to 12 November" gives 12 November.
- A date written without a year uses the year that is nearest to the reference date ("5th January" written in December means next year). A written year is always used.
- A weekday means its next occurrence. `next week` is too vague: it gives no date.
- A time range ("10 AM to 12 PM") uses the start time. A change ("moved from 3 PM to 5 PM") uses the new time. `noon` is 12:00.
- Impossible values (31 February, 13 PM) are `null`, never corrected.

### Events that are only partly known

`event_datetime` needs both a date and a time. With only one of them it stays `null` (nothing is invented), and the literal words are still kept in `date_time_expression`, for example `"12 November"` or `"4 PM"`.

### date_time_expression and description

- `date_time_expression` is the literal date/time wording, for example `"15th October at 5:00 PM"` or `"tomorrow at 11:59 PM"`. It is `null` when the message gives no date or time, or says the deadline is unknown.
- `description` holds notes the title does not: the submission platform ("Submit on Moodle"), the room ("Location: Room 204") and any extra sentences that are not greetings and do not repeat the date or time. It is `null` when there is nothing to add.

### Subject

A subject is first looked up in the `SUBJECTS` list at the top of `nlp/parser.py`. If it is not listed, capitalised words in front of "assignment", "quiz", "exam", "viva", "lab", "lecture", "class" or "project" are used ("Embedded Systems Assignment 2"). Event names such as "placement preparation workshop" are not subjects. The `SUBJECTS` list should be replaced by the real course list.

### Confidence

`confidence` is 0.25 for each core fact found: a title, a type, a date and a time (an event's `event_datetime` supplies both date and time). A message that states its deadline is unknown therefore scores at most 0.5 even though the extraction is correct. This is a baseline score for how complete the extraction is, not a probability.

### Notice and poster text (Step 40)

Text with three or more lines (typical OCR of a notice, circular or poster) is
read with a few extra rules. One-line chat messages behave as before.

- Words such as webinar, session, debate, distribution, orientation, hackathon
  and "an invited talk" make an event only when a date or time is also present.
- "Register now" style buttons and past mentions ("meeting held on ...") are
  ignored when deciding the type. A label such as "Last date for payment: ..."
  makes a task with that date.
- The title comes from the headline (for example "Payment of Fees" gives "Pay
  fees"). An obvious OCR slip in it is fixed only when another line of the same
  text shows the right word; `raw_text` is never changed.
- Times: `8.00 PM`, `09.00 a.m.`, and ranges sharing one am/pm
  (`4.30-5.30 PM`) are read; the start time is used. Day ranges
  (`4th and 5th April 2019`) use the first day and stay in the description.
- Two or more separate dates with no deadline label leave the date empty; all
  are listed in `description`.
- Unchanged: an event with only a time (or only a date) keeps `event_datetime`
  empty and the words stay in `date_time_expression`; "next week" gives no
  date (Steps 38-39); `change_information` stayed `[]` at Step 40 (Steps 41-42 fill it, see below).

### Relative dates (Step 38)

Relative words are turned into a date from the reference date. The output
fields do not change.

| Written | Meaning |
|---|---|
| `in 2 days`, `in 3 weeks`, `in a week` | that many days / weeks after the reference date |
| `day after tomorrow` | reference date + 2 days |
| `Friday` | nearest upcoming Friday (a week away if today is Friday) |
| `this Friday`, `coming Friday` | the upcoming Friday (today counts) |
| `next Friday`, `next week on Friday` | Friday of the following week (weeks run Monday to Sunday) |
| `15/11/2026` | DD/MM/YYYY always (Indian order, never swapped); an impossible date such as `31/02/2026` or `12/25/2026` gives no date |
| `midnight tonight`, `midnight on Sunday` | 00:00 at the end of that day, i.e. the next calendar day |
| `Sunday night`, `tomorrow evening` | the date only; no time is invented (the words stay in `date_time_expression`) |

Still not read: `next week` on its own (no date), `within 3 days`, `this weekend`,
and `midnight` next to an explicit calendar date (it stays on that date at 00:00).
"Tomorrow", weekday and "by Friday" refinements belong to Step 39; change
detection (`change_information`) belongs to Steps 41-42.

#### Day words (Step 39)

| Written | Meaning |
|---|---|
| `tmrw`, `tmr`, `tomorow`, `tommorow` | tomorrow (also in `day after tmrw`) |
| `today evening`, `tomorrow morning` | the date only; the day part stays in `date_time_expression` |
| `this morning`, `this afternoon`, `this evening` | today |
| `by Fri`, `on Mon`, `before Thurs`, `till Tues`, `due Sat`, `next Fri` | short weekday names; accepted only after by / on / before / till / until / due / this / next / coming, so "sat" and "sun" in ordinary sentences are not read as days |

These are still left without a date on purpose: `next week` alone,
`end of the week`, `end of next week`, `this weekend`, `by EOD`, a bare
`by the 15th`, and times with no am/pm such as `at 9`.

### Change detection (Step 41)

Step 41 fills `change_information` when a message announces that something
already announced has changed. It uses the structure of section 9 and adds no
new fields. Every change is one object with these four fields:

| Field | Type | Meaning |
|---|---|---|
| `is_changed` | boolean | Always `true`. Nothing is added when there is no change, so `false` entries never appear. |
| `change_type` | string | What changed: `deadline`, `date`, `time`, `location` or `other` (see below). |
| `old_value` | string / null | The earlier schedule, filled in by Step 42. `null` when the message does not state it. |
| `new_value` | string / null | The new schedule, filled in by Step 42. `null` when the message does not state it. |

When nothing changed the value is `[]`, never `null`. When a message has several
kinds of change there is one object for each kind (see "Several entries").

#### What counts as a change

A change is announced by one of these wordings (letter case does not matter):

| Wording | Examples |
|---|---|
| `rescheduled`, `re-scheduled`, `postponed`, `preponed` | "exam has been postponed", "quiz is now rescheduled to ..." |
| `moved`, `shifted`, `extended`, `advanced`, `changed`, `revised`, `pushed` followed by `from`, `to`, `till`, `until`, `forward`, `back`, `ahead`, `up` or `by` | "deadline extended to 20 November", "moved from Friday to Monday" |
| `has`, `have`, `had`, `is`, `are`, `was`, `were`, `been` or `now`, then optionally `been`, then one of the verbs above | "has been moved", "was changed" |
| `notice of change` | "Notice of change: ..." |
| `date`, `time`, `venue`, `deadline`, `schedule`, `location` or `room` followed by `change`, `changed` or `revised` | "Class venue change: ...", "schedule revised" |
| `change in` / `change of` (optionally with `the`) and then `date`, `time`, `venue`, `deadline`, `schedule` or `location` | "change in the venue" |

These are not changes, so `change_information` stays `[]` for them:

- a request: "Please reschedule the meeting for Monday" (only `rescheduled` counts);
- the same words in another meaning: "Advanced Algorithms lecture on Monday at
  10 AM", "I changed my phone number, submit the form by Friday";
- a notice that is classified as `general_notice` (every field is `null` there,
  including `change_information`), for example "The submission format has
  changed to PDF.";
- wording that is not in the table, such as "Revised date: 12 November".

Only messages that become a task or an event get change entries. The existing
rule that a message with an action verb is a task is unchanged.

#### A changed submission is a task

A change notice with no action verb used to be a general notice. It is now a
task when it contains a change wording, one of the words `submission`,
`assignment`, `report`, `proposal`, `project`, `form`, `fee`, `fees` or
`payment`, and at least one date or time. Example: "Notice of change: Project
proposal submission moved from Friday 5 PM to Monday 5 PM." gives a task with
`due_date` for the new Monday and a `deadline` change. The title drops the
"Notice of change:" label ("Project proposal submission moved"). Without a date
or time, such a notice stays a general notice.

#### Supported change types

| `change_type` | When it is used |
|---|---|
| `deadline` | The message is a task (a submission, something to hand in). One `deadline` entry, even when no date is given, unless only the venue changed. It holds the date and time together. |
| `date` | The message is an event and the date changed. This includes an event with only a new date ("postponed to 3rd November"), and an event postponed or rescheduled with no date at all. |
| `time` | The message is an event and the time changed (the old and the new time differ, or only a new time is given with no date). |
| `location` | The venue changed: "venue change", "room change", "location change", "hall change", or "moved from/to" followed by room, hall, auditorium, lab, laboratory, block, building, classroom or seminar hall. |
| `other` | An event change that names no date, time or place and uses none of the words rescheduled, postponed, preponed or advanced, for example "The workshop schedule has been revised." |

How an event is judged, using the old and new schedule that Step 42 reads:

- `date` is added when both an old and a new date are found and they differ, or
  when a new date is found and the message gives no old date and no old time.
- `time` is added when both an old and a new time are found and they differ, or
  when a new time is found and the message gives no date at all.
- If neither is added, the entry is `date` when the wording is `rescheduled`,
  `postponed`, `preponed` or `advanced`, or a new date exists; otherwise `other`.
- The same date with a new time is only a `time` change: "rescheduled from 10
  November 10 AM to 10 November 2 PM".
- A venue change with at most a stated new schedule is only `location`
  ("Lecture moved from Room 201 to Auditorium on 12 November at 11 AM" does not
  also give a `date` entry). If an old date or time is also stated, the date or
  time entries are added after `location`.

#### Several entries

One entry is added per kind of change, in this order: `location`, then `date`,
then `time` (an event), or `location` then `deadline` (a task, unless only the venue changed). For example
"Operating Systems exam rescheduled from 18 November 10 AM to 20 November 2 PM"
gives a `date` entry and a `time` entry.

#### Effect on the other fields

The contract fields are not changed by Step 41. The top-level `due_date`,
`due_time` and `event_datetime` hold the NEW schedule, because the last date and
the last time in a change message win (see "Dates and times"). The title still
uses the existing change wording ("... rescheduled", "... deadline change").

### Old and new values (Step 42)

Step 42 fills `old_value` and `new_value` of the `deadline`, `date` and `time`
entries.

- The values are the date and time words exactly as the message wrote them, for
  example `"Friday 5 PM"` and `"Monday 5 PM"`. They are never converted to
  `YYYY-MM-DD` or `HH:MM`, and a word such as `tomorrow` stays `tomorrow`.
- A `date` entry holds only the date words, a `time` entry only the time words,
  and a `deadline` entry the date and the time together. If the date and the
  time are more than 15 characters apart, or a full stop, `;`, `!`, `?` or a
  new line is between them, they are joined with a comma. Only the first date
  and the first time of each part are used.
- `old_value` is `null` when the message does not state the earlier schedule.
  The parser reads one message at a time and has no memory of earlier notices,
  so it never fills the old value in from anywhere else.
- `location` and `other` entries always have `null` for both values.

#### Where the values come from

Only the sentence that contains the first change wording is read (a full stop
followed by a space, `;` or a new line ends a sentence). Inside it:

1. `from X to Y` after the change word (also `till` or `until` instead of `to`)
   gives the old value from X and the new value from Y. It is used only when no
   date or time stands between the change word and `from`.
2. `to Y from X` after the change word (`till`, `until` and `for` also work)
   gives the new value from Y and the old value from X. It is used only when X
   contains a date.
3. Otherwise the new value comes from the words after the change word and the
   old value from the words before it in the same sentence ("quiz originally at
   10 AM moved to 12 PM" gives the old time 10 AM). A word such as "originally"
   is not needed: any date or time before the change word counts as the old one.

| Message | Entries (`change_type`, `old_value`, `new_value`) |
|---|---|
| Update: the Web Technologies project deadline has moved from 8 November to 12 November 2026. | `deadline`, `8 November`, `12 November 2026` |
| The Machine Learning assignment deadline has been postponed from 10 November to 15 November at 5 PM. | `deadline`, `10 November`, `15 November at 5 PM` |
| Notice of change: Project proposal submission moved from Friday 5 PM to Monday 5 PM. | `deadline`, `Friday 5 PM`, `Monday 5 PM` |
| Submit the lab report. Deadline extended to 20 November. | `deadline`, `null`, `20 November` |
| Update: Operating Systems exam rescheduled from 18 November 10 AM to 20 November 2 PM in Hall C. | `date`, `18 November`, `20 November`; `time`, `10 AM`, `2 PM` |
| The Computer Architecture quiz originally at 10 AM moved to 12 PM on 11 November. | `time`, `10 AM`, `12 PM` |
| The Computer Architecture quiz originally planned for 9 November is now rescheduled to 11 November 2026 at 12 PM. | `date`, `9 November`, `11 November 2026` |
| The Operating Systems mid-sem exam has been postponed to 3rd November, 2 PM. | `date`, `null`, `3rd November` |
| Quiz rescheduled to 12 November from 10 November | `date`, `10 November`, `12 November` |
| Seminar rescheduled from tomorrow to Friday | `date`, `tomorrow`, `Friday` |
| The DBMS exam has been postponed. | `date`, `null`, `null` |
| Class venue change: Database lecture moved from Room 201 to Auditorium on 12 November at 11 AM. | `location`, `null`, `null` |

Two cases that look like changes but are read more carefully:

- A time range after a new date is not a change of time: "Quiz rescheduled to
  12 November, from 10 AM to 12 PM" gives only `date`, `null`, `12 November`.
- A bare day number is not a date: in "Quiz moved from 8 to 12 November" the
  old value is `null` and the new value is `12 November`.

### Known limitations

- Change detection recognises only the wordings listed under "What counts as a change". Other wordings ("Revised date: 12 November", "new date will be ...") give `[]`.
- Only the sentence with the first change wording is read for `change_type` and for the old and new values. A second change in the same message gets no entry of its own: "Quiz rescheduled to Friday at 3 PM. Exam postponed to 20 November." gives one `date` entry with the new value `Friday`.
- The old value is `null` unless the message states it, because the parser has no memory of earlier notices. Any date or time that stands before the change word in the same sentence is taken as the old schedule, even if it is not really the old one.
- The `from X to Y` pattern is used to extract old and new values only when no date or time appears between the change word and `from`.
- Values are the original words, not converted. Times written without am/pm ("at 9") are not read, so they are never a value. `location` and `other` entries have `null` values, and a bare day number ("from 8 to 12 November") is not a date.
- A change message is still one task or event: the top-level fields hold the last date and the last time of the whole message.
- Numeric dates are supported in DD/MM/YYYY format. `next Friday` refers to Friday of the following week, and midnight expressions are supported as described in Step 38.
- One message produces one task or event. A message that lists several tasks gets only the first signal's title and the last date and time.
- OCR text is processed in the same way, but the OCR-to-NLP connection is Steps 36-37.

### Running the tests

From the repository root:

```
python -m unittest discover -s nlp -p "test_*.py" -v
python -m nlp.evaluate_step21
```

The second command scores the 25 Step 21 dataset cases stored in `nlp/test_data/step21_dataset.json`. The dataset is owned by the Step 21 / Step 66 evaluation work; the JSON file is a copy of the workbook's "Test Dataset" sheet. Pass `--xlsx FILE` to read the original Excel file instead (needs `pip install openpyxl`).
