# NUDGE Data Dictionary
**Phase 7: Database & Data Layer — Step 45**
**Authoritative Contract Reference:** `PROJECT.md` — Shared Structured JSON / Data Contract (Step 3)
**Schema Implementation:** `backend/database/schema.sql` (Step 43)
**Constraint Specification:** `docs/database_constraints.md` (Step 44)

---

## 1. Overview & Purpose

This document serves as the formal **Data Dictionary** for the NUDGE Intelligent Student Life Management Platform. It defines the exact semantic meaning, data types, nullability, ownership boundaries, and validation rules for all **19 fields** in the agreed Shared Structured JSON / Data Contract.

All components in the platform (NLP parser, OCR ingestion, database repository, ML priority engine, workload/productivity analytics, and frontend dashboard) must strictly adhere to these definitions.

---

## 2. Core 19-Field Data Dictionary Table

| Field Name | Meaning | Contract Data Type / Expected Format | Database Type (SQLite) | Nullable? | Owning Module / Layer | Rules, Defaults, or Validation Notes |
|---|---|---|---|---|---|---|
| `task_id` | Unique identifier assigned to the task upon storage persistence. | `integer / string` (initially `null` in unpersisted payloads) | `INTEGER` | **No** (in DB)<br>*Nullable in transit* | **Task / Storage Layer** | Primary key with autoincrement. Assigned sequentially by the storage layer on insert. Never invented by NLP or modified by caller. |
| `task_title` | Actionable title or concise summary of the task. | `string` | `TEXT` | **No** | **NLP Module** | Required headline extracted from text. Cannot be empty or whitespace-only (`CHECK (length(trim(task_title)) > 0)`). |
| `description` | Detailed instructions, submission guidelines, or additional context. | `string / null` | `TEXT` | **Yes** | **NLP Module** | Optional. Must remain `null` if no additional description or context exists in the source text. Never invented. |
| `task_type` | Classified category of the task or scheduled academic event. | `string` | `TEXT` | **No** | **NLP Module** | Required classification (e.g., `'assignment'`, `'exam'`, `'quiz'`, `'project'`, `'viva'`, `'class'`, `'meeting'`, `'event'`). Cannot be blank. |
| `subject` | Academic course name or course code associated with the task. | `string / null` | `TEXT` | **Yes** | **NLP Module** | Optional course identifier (e.g., `'Machine Learning'`, `'DBMS'`, `'CS301'`). Must remain `null` if unstated in the source text. |
| `due_date` | Raw due or submission date extracted directly from the message text. | `string (YYYY-MM-DD) / null` | `TEXT` | **Yes** | **NLP Module** | Preserves raw date extracted by NLP. Format: ISO date `YYYY-MM-DD`. Must remain `null` if no date is present in text. |
| `due_time` | Raw due or submission time extracted directly from the message text. | `string (HH:MM) / null` | `TEXT` | **Yes** | **NLP Module** | Preserves raw time extracted by NLP in 24-hour format (`HH:MM`). Must remain `null` if no time is present in text. |
| `due_datetime` | Normalized ISO 8601 timestamp representing the final submission deadline. | `string (ISO 8601) / null`<br>`YYYY-MM-DDTHH:MM:SS` | `TEXT` | **Yes** | **Task / Storage Layer** | Normalized by storage layer by combining `due_date` and `due_time`. **Populated only when both date and time exist.** If `due_time` is missing, `due_datetime` must remain `null` (no end-of-day time like 23:59 is invented). Consumed by ML priority and workload engines. |
| `event_datetime` | Scheduled datetime when a live event (exam, lecture, viva, meeting) occurs. | `string (ISO 8601) / null`<br>`YYYY-MM-DDTHH:MM:SS` | `TEXT` | **Yes** | **NLP Module**<br>*(Storage validates)* | Represents scheduled occurrences rather than submission deadlines. NLP extracts event date/time; storage validates format before persistence. Must remain `null` for non-event tasks. |
| `status` | Authoritative lifecycle status of the task in the management platform. | `string` (default: `"pending"`) | `TEXT` | **No** | **Task / Storage Layer** | Default: `'pending'`. Permitted values: `'pending'`, `'in_progress'`, `'completed'`, `'cancelled'`. Authoritative control belongs exclusively to the storage layer; NLP must never infer `'completed'` or `'overdue'` from message content. |
| `importance` | Explicit importance rating stated in the notice or configured by the student. | `integer / string / null` | `TEXT` | **Yes** | **Shared / NLP / Storage Layer** | Evaluated by ML priority engine against `'high'`, `'medium'`, `'low'` (case-insensitive). Must remain `null` if unstated; never defaulted to a middle value. |
| `estimated_effort` | Expected duration or workload required to complete the task. | `string / number / null` | `NUMERIC` | **Yes** | **Shared / NLP / Storage Layer** | Non-negative numeric value (hours/minutes). `CHECK (estimated_effort IS NULL OR estimated_effort >= 0)`. Summed in ML workload analytics only when numeric. Unknown effort must remain `null` (missing effort $\neq$ zero effort). |
| `source` | Origin channel, platform, or ingest modality of the message. | `string` | `TEXT` | **No** | **NLP Module** | Provenance identifier (e.g., `'LMS Notice'`, `'Email'`, `'WhatsApp'`, `'Screenshot/OCR'`). Cannot be empty (`CHECK (length(trim(source)) > 0)`). |
| `raw_text` | Unmodified, unparsed input text or OCR detection string. | `string` | `TEXT` | **No** | **NLP Module** | Full raw message text preserved for auditing, re-parsing, and change detection. Cannot be empty (`CHECK (length(trim(raw_text)) > 0)`). |
| `date_time_expression` | Literal verbatim date/time phrase identified within the raw source text. | `string / null` | `TEXT` | **Yes** | **NLP Module** | Preserves literal text expressions (e.g., `'tomorrow at 5 PM'`, `'by 15th October'`). Must remain `null` if no explicit phrase was matched. |
| `confidence` | NLP parser extraction confidence score. | `float (0.0 – 1.0)` | `REAL` | **No** | **NLP Module** | Confidence score between `0.0` and `1.0`. Default: `0.0`. Validated by `CHECK (confidence >= 0.0 AND confidence <= 1.0)`. |
| `change_information` | Array of detected modifications against previous notices or records. | `array of objects`<br>(default: `[]`) | `TEXT` *(JSON Array)* | **No** | **NLP Module** | Default: `'[]'`. Validated as a valid JSON array (`CHECK (json_valid(change_information) AND json_type(change_information) = 'array')`). Must be empty array `[]` when no change is detected. |
| `created_at` | Timestamp when the task record was created in the storage layer. | `string (ISO 8601)`<br>`YYYY-MM-DDTHH:MM:SS` | `TEXT` | **No** | **Task / Storage Layer** | Generated automatically on insertion using local ISO 8601 format (`strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')`). Immutable. |
| `completed_at` | Timestamp when the task was marked completed. | `string (ISO 8601) / null`<br>`YYYY-MM-DDTHH:MM:SS` | `TEXT` | **Yes** | **Task / Storage Layer** | Managed by the storage/repository layer. Recorded when `status` transitions to `'completed'`. Cleared to `null` if task is reopened (`status` reverted to `'pending'` or `'in_progress'`). Consumed by productivity metrics. |

---

## 3. Temporal Semantics & Deadline vs. Event Distinctions

To prevent scheduling clashes and deadline confusion, the platform strictly separates four temporal fields:

```text
Temporal Fields in NUDGE:

1. due_date (NLP)        ──> Raw date extracted: "2026-10-15"
2. due_time (NLP)        ──> Raw time extracted: "17:00"
                                     │
                                     ▼ (Normalized by Storage Layer ONLY if both exist)
3. due_datetime (Storage) ──> "2026-10-15T17:00:00" (Submission Deadline)

4. event_datetime (NLP)   ──> "2026-10-15T10:00:00" (Exam/Class/Meeting Occurrence)
```

### Detailed Differences
* **`due_date` vs. `due_datetime`**:
  * `due_date` contains only the date component extracted by NLP (`YYYY-MM-DD`). It does not specify when during that day the item is due.
  * `due_datetime` is the unified ISO 8601 string (`YYYY-MM-DDTHH:MM:SS`) required by downstream intelligence modules for countdown and overdue urgency calculations.
* **Strict Missing Deadline Rule**:
  * If a notice states *"Assignment due on 15th October"* with no time specified, `due_date` is `"2026-10-15"` and `due_time` is `null`.
  * In this scenario, `due_datetime` **must remain `null`**. The storage layer does **not** assume `23:59:00` or any other invented cutoff unless an explicit end-of-day convention is formally agreed upon.
* **`due_datetime` vs. `event_datetime`**:
  * `due_datetime` represents a **submission cutoff** (e.g., uploading an assignment, submitting a project report). Work is performed *before* this timestamp.
  * `event_datetime` represents an **in-person or live synchronous occurrence** (e.g., an exam sitting, a viva presentation, a lecture, or a club meeting). The student must be present *at* this timestamp.
  * Keeping them in separate fields prevents calendar events from triggering misleading submission-overdue warnings.

---

## 4. `change_information` Structure & Semantics

When messages update prior notices (e.g., rescheduled deadlines, postponed exams, room changes), NLP detects the change and encodes it into the `change_information` array.

### Schema of Change Objects
Each element in the `change_information` array is an object with four mandatory keys:
* **`is_changed`** (`boolean`): Flag indicating whether an active modification was identified (`true` or `false`).
* **`change_type`** (`string`): Category of the property being modified. Permitted values: `'deadline'`, `'date'`, `'time'`, `'location'`, `'other'`.
* **`old_value`** (`string / null`): Prior value before the notice, if known from context or history (e.g., `'Wednesday 11:59 PM'`, `'Room 101'`, `null`).
* **`new_value`** (`string / null`): Updated value announced in the current message (e.g., `'Friday 11:59 PM'`, `'Room 204'`, `null`).

### Rules:
1. **Always an Array**: If no change is detected, `change_information` **must be `[]`** (never `null` or `{}`).
2. **Multiple Changes**: If a notice announces both a date change and a venue change, the array contains multiple change objects:
   ```json
   [
     {
       "is_changed": true,
       "change_type": "date",
       "old_value": "2026-10-15",
       "new_value": "2026-10-18"
     },
     {
       "is_changed": true,
       "change_type": "location",
       "old_value": "Room 101",
       "new_value": "Auditorium"
     }
   ]
   ```

---

## 5. Timestamp & Timezone Conventions

* **Format**: All database timestamps (`created_at`, `completed_at`, `due_datetime`, and `event_datetime`) use **ISO 8601 extended format in naive local time: `YYYY-MM-DDTHH:MM:SS`**.
* **Rationale & Compatibility**:
  * `ml/priority_engine.py` converts strings using `datetime.fromisoformat()`. It explicitly checks `(due_datetime.utcoffset() is None) != (current_time.utcoffset() is None)` and returns `None` if one timestamp has a timezone offset while the other is naive.
  * `ml/intelligence_metrics.py` calculates elapsed time using `datetime.now()`, which generates naive local datetimes. Subtracting timezone-aware datetimes from naive datetimes triggers a Python `TypeError`.
  * Standardizing on naive local ISO 8601 ensures seamless calculations across all analytics engines without timezone mismatch exceptions.

---

## 6. Ownership & Boundary Separation

The 19 fields are owned and maintained across clearly defined module boundaries:

```text
┌────────────────────────────────────────────────────────┐
│ NLP Module Extracts & Provides:                        │
│   • task_title          • description                  │
│   • task_type           • subject                      │
│   • due_date            • due_time                     │
│   • event_datetime      • date_time_expression         │
│   • source              • raw_text                     │
│   • confidence          • change_information           │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Task / Storage Layer Maintains & Normalizes:           │
│   • task_id (generated) • due_datetime (normalized)    │
│   • status (authoritative)                             │
│   • created_at (insert) • completed_at (transition)    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Shared / Configured Fields:                            │
│   • importance          • estimated_effort             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Intelligence Layer Computes Dynamically (NOT stored):  │
│   • priority_score      • priority_label               │
│   • priority_reason     • workload metrics             │
│   • productivity metrics• risk signals                 │
└────────────────────────────────────────────────────────┘
```

---

## 7. Database Implementation Details (SQLite)

The following constraints are database-level enforcement mechanisms in SQLite (`backend/database/schema.sql`) designed to protect data integrity:
* **Primary Key**: `task_id INTEGER PRIMARY KEY AUTOINCREMENT`.
* **Status Domain**: `CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled'))`.
* **Confidence Range**: `CHECK (confidence >= 0.0 AND confidence <= 1.0)`.
* **JSON Array Validation**: `CHECK (json_valid(change_information) AND json_type(change_information) = 'array')` using SQLite's native JSON1 extension.
* **Non-Negative Effort**: `CHECK (estimated_effort IS NULL OR estimated_effort >= 0)`.
* **Non-Empty Text**: `CHECK (length(trim(field)) > 0)` on `task_title`, `task_type`, `source`, and `raw_text`.
