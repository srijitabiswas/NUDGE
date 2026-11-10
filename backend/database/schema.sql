-- ============================================================================
-- NUDGE — From Messages to Actions: Intelligent Student Life Management Platform
-- Phase 7: Database & Data Layer
-- Step 43: Formal Database Schema / Design
-- Target Database: SQLite 3 (Python built-in sqlite3)
-- Contract Reference: PROJECT.md — Shared Structured JSON / Data Contract (Step 3)
-- ============================================================================
--
-- Key Schema Rules & Design Decisions:
-- 1. All 19 fields from the Step 3 Data Contract are preserved with exact types,
--    ownership, and nullability constraints.
-- 2. Datetime Convention: All stored timestamps and datetimes (created_at,
--    completed_at, due_datetime, event_datetime) use standardized ISO 8601
--    extended format in naive local time ('YYYY-MM-DDTHH:MM:SS') for 100%
--    compatibility with downstream ML intelligence modules and tests.
-- 3. due_datetime Normalization: Derived strictly when both due_date ('YYYY-MM-DD')
--    and due_time ('HH:MM') are available. If due_time is missing, due_datetime
--    remains NULL; no end-of-day time (e.g. 23:59) is invented.
-- 4. event_datetime: Represents scheduled events (exams, lectures, vivas, meetings),
--    distinct from submission deadlines (due_datetime). Validated by storage.
-- 5. Status Authority & completed_at Lifecycle: The task/storage layer is
--    authoritative for task status. completed_at is recorded when status transitions
--    to 'completed', and cleared (set to NULL) if a completed task is reopened.
-- 6. change_information: Stored as a JSON-serialized text array (default '[]').
--    Enforced via SQLite JSON1 functions json_valid() and json_type().
-- 7. Missing Information: Explicitly represented as NULL, never invented.
-- ============================================================================

CREATE TABLE IF NOT EXISTS tasks (
    -- 1. Identity (Owned and assigned by Storage Layer upon insertion)
    task_id                 INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 2. Core Content & Classification (NLP Module)
    task_title              TEXT NOT NULL CHECK (length(trim(task_title)) > 0),
    description             TEXT,                                                -- Nullable: context / instructions
    task_type               TEXT CHECK (task_type IS NULL OR length(trim(task_type)) > 0),    -- 'assignment', 'exam', 'quiz', 'project', 'event', etc.
    subject                 TEXT,                                                -- Nullable: course name or subject code

    -- 3. Temporal Extractions & Normalization (NLP + Storage Layer)
    due_date                TEXT,                                                -- Nullable: raw NLP extracted date ('YYYY-MM-DD')
    due_time                TEXT,                                                -- Nullable: raw NLP extracted time ('HH:MM')
    due_datetime            TEXT,                                                -- Nullable: normalized ISO 8601 ('YYYY-MM-DDTHH:MM:SS')
    event_datetime          TEXT,                                                -- Nullable: scheduled event datetime ('YYYY-MM-DDTHH:MM:SS')
    date_time_expression    TEXT,                                                -- Nullable: raw literal text phrase (e.g., '15th October at 5:00 PM')

    -- 4. Authoritative Task Status (Storage Layer)
    status                  TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),

    -- 5. Optional Effort & Importance (Shared / NLP / Storage Layer)
    importance              TEXT,                                                -- Nullable: 'high', 'medium', 'low' or explicit rating
    estimated_effort        NUMERIC CHECK (estimated_effort IS NULL OR estimated_effort >= 0), -- Nullable: numeric effort (hours/minutes)

    -- 6. Provenance & Extraction Metadata (NLP Module)
    source                  TEXT NOT NULL CHECK (length(trim(source)) > 0),       -- 'LMS Notice', 'WhatsApp', 'Email', 'Screenshot/OCR'
    raw_text                TEXT NOT NULL CHECK (length(trim(raw_text)) > 0),     -- Original unstructured input text
    confidence              REAL NOT NULL DEFAULT 0.0
                            CHECK (confidence >= 0.0 AND confidence <= 1.0),      -- Extraction confidence bound

    -- 7. Change Tracking (NLP Module)
    change_information      TEXT NOT NULL DEFAULT '[]'
                            CHECK (json_valid(change_information) AND json_type(change_information) = 'array'),

    -- 8. Storage Lifecycle Timestamps (Storage Layer)
    created_at              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    completed_at            TEXT                                                 -- Nullable: recorded on completion, cleared if reopened
);

-- ============================================================================
-- Indexes for Frequent Query Patterns
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_datetime ON tasks(due_datetime);
CREATE INDEX IF NOT EXISTS idx_tasks_event_datetime ON tasks(event_datetime);
CREATE INDEX IF NOT EXISTS idx_tasks_subject ON tasks(subject);


-- ============================================================================
-- OCR metadata (Step 47)
-- Confidence details for tasks that came from a screenshot. Kept in its own
-- table so the 19-field tasks contract is unchanged. The NLP confidence stays
-- in tasks.confidence and is never mixed with OCR confidence.
-- ============================================================================
CREATE TABLE IF NOT EXISTS ocr_metadata (
    ocr_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id             INTEGER NOT NULL UNIQUE
                        REFERENCES tasks(task_id) ON DELETE CASCADE,
    image_filename      TEXT NOT NULL CHECK (length(trim(image_filename)) > 0),
    overall_confidence  REAL
                        CHECK (overall_confidence IS NULL
                               OR (overall_confidence >= 0.0 AND overall_confidence <= 1.0)),
    line_confidences    TEXT NOT NULL DEFAULT '[]'
                        CHECK (json_valid(line_confidences)
                               AND json_type(line_confidences) = 'array'),
    created_at          TEXT NOT NULL
                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
);
