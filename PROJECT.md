# From Messages to Actions — Intelligent Student Life Management Platform

## 1. Project Overview

From Messages to Actions is an intelligent student life management platform designed to convert scattered student information into structured, actionable information.

The system processes permitted sources such as messages, emails, LMS notices, screenshots, and university notices. It extracts tasks, deadlines, events, and related information, stores the structured information, analyzes workload and priority, and presents useful information through a unified student dashboard with alerts.

### Core Pipeline

Message
↓
NLP
↓
Structured Data
↓
Storage
↓
Priority + Analytics
↓
Dashboard
↓
Alerts

Screenshot
↓
OCR
↓
Text
↓
NLP
↓
Structured Data


## 2. Problem Statement

Students receive important academic and administrative information through multiple scattered sources such as messages, emails, LMS notices, screenshots, and university announcements.

Important tasks, deadlines, examinations, events, and changes can therefore be difficult to track consistently.

The proposed system aims to convert such unstructured information into structured student-life information and provide prioritization, analytics, reminders, and proactive assistance through a unified platform.


## 3. Phase 1 Scope

### 3.1 Phase 1 Features

1. AI Message & Notice Parser
2. Screenshot-to-Action / OCR
3. Smart Task & Deadline Manager
4. Google Calendar Synchronization
5. AI Priority Recommendation
6. "Did You Forget Something?"
7. "What Did I Miss?" AI Digest
8. Change Detection
9. Source Reliability & Conflict Detection
10. Early Risk Detection using ML
11. Unified Student Dashboard
12. Assignment & Exam Tracker
13. Performance & Productivity Analytics
14. Personalized Notification Engine
15. Proactive Alerts


### 3.2 Functional in the 5-Day Milestone

The following must have a working implementation or functional integration:

- AI Message & Notice Parser
- Screenshot-to-Action / OCR
- Smart Task & Deadline Manager
- AI Priority Recommendation
- Unified Student Dashboard
- Assignment & Exam Tracker
- Performance & Productivity Analytics
- Personalized Notification Engine
- Proactive Alerts

The underlying storage and integration pipeline required to connect these components is also part of the milestone.


### 3.3 Baseline / Prototype

The following may be implemented initially as baseline or prototype functionality:

- "Did You Forget Something?"
- "What Did I Miss?" AI Digest
- Change Detection
- Source Reliability & Conflict Detection
- Early Risk Detection using ML

The goal for these features is an initial technically valid baseline rather than sophisticated intelligence.


### 3.4 Deferred from the 5-Day Critical Path

The following should not delay the core implementation:

- Google Calendar Synchronization
- Sophisticated personalized intelligence beyond the initial baseline

The priority is to establish a real end-to-end pipeline before adding secondary integrations or advanced intelligence.


## 4. Team Responsibilities

| Member | Responsibility | Inputs | Outputs | Dependencies |
|---|---|---|---|---|
| Prakriti | NLP/message parser, task extraction, date/time extraction, event extraction, intent/type classification, confidence, change-related extraction | Messages, notices, OCR text | Structured task/event information | Shared data contract |
| Neha | OCR, screenshot-to-action, image preprocessing | Screenshots/images | Extracted text | Shared data contract; later NLP integration |
| Sresthita | Priority recommendation, workload calculation, productivity analytics, early-risk baseline | Structured task information | Priority, workload and analytics outputs | Structured data from NLP/OCR pipeline |
| Srijita | Frontend, unified dashboard, task interface, assignment/exam tracker, priority/analytics display, alert UI | Structured data, intelligence outputs | Student-facing dashboard and interfaces | Shared data contract; integrated outputs |
| Rumana | Database/schema formalization, dataset preparation, data dictionary, test cases, evaluation framework, evaluation/results documentation | Actual implementation outputs and shared data contract | Formal schema, datasets, tests, evaluation | Later-stage integration; must not block initial development |


## 5. System Architecture

### Primary Pipeline

Message
↓
NLP
↓
Structured Data
↓
Storage
↓
Intelligence
↓
Dashboard
↓
Alerts


### Screenshot Pipeline

Screenshot
↓
OCR
↓
Text
↓
NLP
↓
Structured Data
↓
Storage


### Intelligence Layer

The intelligence layer consumes structured information to support:

- Priority recommendation
- Workload calculation
- Productivity analytics
- Early-risk baseline
- Change detection
- Source reliability/conflict analysis
- Notification and proactive alert generation


## 6. Dependency Flow

The initial development work is intentionally parallel.

```text
                         START
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      PRAKRITI           NEHA          SRESTHITA
         NLP              OCR        Priority/Analytics
          |                |                |
          |                v                |
          |          OCR -> NLP             |
          |                |                |
          +---------> STRUCTURED DATA <-----+
                           |
                           v
                        STORAGE
                           |
                           v
                        SRIJITA
                   Unified Dashboard
                           |
                           v
                    Alerts/Analytics
                           |
                           v
                   CORE INTEGRATION
                           |
                           v
                        RUMANA
             Database Formalization
             Testing + Evaluation
```


## Phase 1 Data Requirements

| # | Feature | Owner | Input | Required Data | Output | Needs From |
|---|---|---|---|---|---|---|
| 1 | AI Message & Notice Parser | Prakriti | Messages, notices, OCR text | Message/notice text, OCR text content | Structured task/event information | User / External sources (messages, notices), Neha (OCR text) |
| 2 | Screenshot-to-Action / OCR | Neha | Screenshots/images | Screenshot/image content | Extracted text | User (screenshots/images) |
| 3 | Smart Task & Deadline Manager | TBD/Shared (Task Interface: Srijita) | Structured task/event information, user actions | Tasks, deadlines, events, task status updates | Structured task and deadline data, task statuses | Prakriti (NLP) / Srijita (task interface) |
| 4 | Google Calendar Synchronization | TBD/Shared | TBD/Shared (Deferred) | TBD/Shared (Deferred) | TBD/Shared (Deferred) | TBD/Shared (Deferred from 5-day critical path; non-blocking) |
| 5 | AI Priority Recommendation | Sresthita | Structured task information | Tasks, deadlines, task status, task type, importance, and estimated effort (if available) | Priority score, priority label, and explanation/reason | Prakriti (NLP) / Storage |
| 6 | "Did You Forget Something?" | TBD/Shared | Structured task information (TBD/Shared) | Pending tasks, deadlines, completion status (TBD/Shared) | Reminder / alert outputs (TBD/Shared) | Prakriti (NLP) / Storage (TBD/Shared) |
| 7 | "What Did I Miss?" AI Digest | TBD/Shared | Structured task/event information, notice history (TBD/Shared) | Recent notices, tasks, events, deadlines (TBD/Shared) | Digest summary outputs (TBD/Shared) | Prakriti (NLP) / Storage (TBD/Shared) |
| 8 | Change Detection | Prakriti | Messages, notices, OCR text, structured data | Updated notices/messages, existing structured task/event data | Change-related extraction / detected changes | Prakriti (NLP), Storage / User |
| 9 | Source Reliability & Conflict Detection | TBD/Shared | Structured information, source metadata (TBD/Shared) | Source origin/type, conflicting task/event information (TBD/Shared) | Reliability scores, conflict detection outputs (TBD/Shared) | Prakriti (NLP) / Storage (TBD/Shared) |
| 10 | Early Risk Detection using ML | Sresthita | Structured task information | Tasks, deadlines, workload information | Early-risk baseline outputs | Prakriti (NLP) / Storage |
| 11 | Unified Student Dashboard | Srijita | Structured data, intelligence outputs | Structured tasks/events, priority scores, analytics, alerts | Student-facing dashboard and interfaces | Prakriti (NLP), Sresthita (Priority/Analytics), Storage, Intelligence Layer |
| 12 | Assignment & Exam Tracker | Srijita | Structured data | Assignments, examinations, deadlines, dates | Student-facing assignment and exam tracker interface | Prakriti (NLP) / Storage |
| 13 | Performance & Productivity Analytics | Sresthita (Analytics) / Srijita (Display) | Structured task information | Tasks, deadlines, workload and completion records | Workload calculation and productivity analytics outputs | Prakriti (NLP) / Storage |
| 14 | Personalized Notification Engine | TBD/Shared (Alert UI: Srijita) | Structured data, intelligence outputs (TBD/Shared) | Tasks, deadlines, priority recommendations, alerts (TBD/Shared) | Personalized notification outputs (TBD/Shared) | Storage, Intelligence Layer (Sresthita / TBD/Shared) |
| 15 | Proactive Alerts | TBD/Shared (Alert UI: Srijita) | Structured data, intelligence outputs (TBD/Shared) | Upcoming deadlines, risk baseline, priority recommendations (TBD/Shared) | Proactive alert outputs and alert UI | Storage, Intelligence Layer (Sresthita / TBD/Shared) |

## Shared Structured JSON / Data Contract

### Agreed Structure

```json
{
  "task_id": null,
  "task_title": "",
  "description": null,
  "task_type": "",
  "subject": null,
  "due_date": null,
  "due_time": null,
  "due_datetime": null,
  "event_datetime": null,
  "status": "pending",
  "importance": null,
  "estimated_effort": null,
  "source": "",
  "raw_text": "",
  "date_time_expression": null,
  "confidence": 0.0,
  "change_information": [],
  "created_at": null,
  "completed_at": null
}
```

### Component Ownership

- **Task/storage layer owns:**
  - `task_id`
  - `due_datetime` normalization
  - authoritative `status`
  - `created_at`
  - `completed_at`

- **NLP provides/extracts:**
  - `task_title`
  - `description`
  - `task_type`
  - `subject`
  - `due_date`
  - `due_time`
  - `event_datetime`
  - `source`
  - `raw_text`
  - `date_time_expression`
  - `confidence`
  - `change_information`

- **Optional fields:**
  - `importance`
  - `estimated_effort`
  *(These may be extracted from the source when available or provided/maintained elsewhere.)*

- **Intelligence layer calculates rather than receives as input:**
  - `priority_score`
  - `priority_label`
  - `priority_reason`
  - `workload metrics`
  - `productivity metrics`
  - `risk signals`

### Field Definitions

> **Note on "Required" Fields**: A required field must be present in the contract, but its value may be `null` when the information is unavailable, unless a default is explicitly defined. Status defaults to `"pending"` as already documented.

| Field | Type | Requirement / Nullability | Owner | Description |
|---|---|---|---|---|
| `task_id` | integer / string | Nullable | Task/storage layer | Unique identifier assigned by the storage layer upon creation. |
| `task_title` | string | Required | NLP | Extracted task title or action headline. |
| `description` | string | Optional / Nullable | NLP | Detailed description, instructions, or notes. |
| `task_type` | string | Required | NLP | Classified task type (e.g., assignment, exam, quiz, event). |
| `subject` | string | Optional / Nullable | NLP | Course or subject name/code. |
| `due_date` | string (YYYY-MM-DD) | Optional / Nullable | NLP | Raw submission/due date extracted from text. |
| `due_time` | string (HH:MM) | Optional / Nullable | NLP | Raw submission/due time extracted from text. |
| `due_datetime` | string (ISO 8601) | Optional / Nullable | Task/storage layer | Normalized datetime used by downstream intelligence. |
| `event_datetime` | string (ISO 8601) | Optional / Nullable | NLP | Scheduled datetime for an event (exam, viva, class, meeting), distinct from submission deadline. NLP extracts the event date/time from the source text and provides event_datetime in ISO 8601 format when sufficient information is available; the task/storage layer validates it and handles any final normalization or timezone handling before persistence. |
| `status` | string | Required (default: `"pending"`) | Task/storage layer | Authoritative status managed by task/storage layer. |
| `importance` | integer / string | Optional / Nullable | NLP / Task-storage layer | Importance level if stated in source or provided elsewhere. |
| `estimated_effort` | string / number | Optional / Nullable | NLP / Task-storage layer | Expected completion effort/duration if stated or provided elsewhere. |
| `source` | string | Required | NLP | Source channel or platform (e.g., LMS, email, notice, screenshot). |
| `raw_text` | string | Required | NLP | Original unstructured message or notice text. |
| `date_time_expression` | string | Optional / Nullable | NLP | Literal date/time phrase extracted from the raw text. |
| `confidence` | float (0.0 - 1.0) | Required | NLP | Confidence score of the extraction. |
| `change_information` | array of objects | Required (defaults to `[]`) | NLP | Array of detected changes; empty array if no change is detected. |
| `created_at` | string (ISO 8601) | Nullable | Task/storage layer | Timestamp when the task was created; owned and maintained by the task/storage layer. |
| `completed_at` | string (ISO 8601) | Nullable | Task/storage layer | Timestamp when the task was marked completed; owned and maintained by the task/storage layer. |

### Important Rules

- Missing/unknown information must be represented as `null`, not invented.
- A required field must be present in the contract, but its value may be `null` when the information is unavailable, unless a default is explicitly defined. Status defaults to `"pending"` as already documented.
- NLP must not infer `completed` or `overdue` merely from message content.
- The task/storage layer is authoritative for task status.
- `created_at` and `completed_at` are owned and maintained by the task/storage layer.
- `due_date` and `due_time` preserve NLP extraction, while `due_datetime` is the normalized datetime used by downstream intelligence.
- `event_datetime` represents an event such as an exam, viva, class, meeting, or other scheduled event and is separate from a submission deadline.
- `change_information` must be an array. It can contain multiple change objects. If no change is detected, it must be `[]`.
- Each change object should contain `is_changed`, `change_type`, `old_value`, and `new_value`.
- `change_type` may include values such as `deadline`, `date`, `time`, `location`, or `other`.

### Example Transformation

**Incoming Student Message:**
> *"Dear Students, please submit your Machine Learning Assignment 1 on Moodle by 15th October at 5:00 PM."*

**Structured Contract Output:**
```json
{
  "task_id": null,
  "task_title": "Submit Machine Learning Assignment 1",
  "description": "Submit on Moodle",
  "task_type": "assignment",
  "subject": "Machine Learning",
  "due_date": "2026-10-15",
  "due_time": "17:00",
  "due_datetime": "2026-10-15T17:00:00",
  "event_datetime": null,
  "status": "pending",
  "importance": null,
  "estimated_effort": null,
  "source": "LMS Notice",
  "raw_text": "Dear Students, please submit your Machine Learning Assignment 1 on Moodle by 15th October at 5:00 PM.",
  "date_time_expression": "15th October at 5:00 PM",
  "confidence": 0.95,
  "change_information": [],
  "created_at": null,
  "completed_at": null
}
```
