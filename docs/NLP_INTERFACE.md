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