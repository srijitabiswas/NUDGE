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
