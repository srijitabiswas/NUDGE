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
| 5 | AI Priority Recommendation | Sresthita | Structured task information | Tasks, deadlines, event details | Priority recommendation outputs | Prakriti (NLP) / Storage |
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
