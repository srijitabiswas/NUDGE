# Intelligence Module — Input/Output Interface

**Project:** NUDGE — From Messages to Actions  
**Owner:** Sresthita Nath  
**Status:** Draft for team review

## 1. Purpose

The Intelligence module consumes structured task information from the storage/task layer and produces priority recommendations, workload calculations, productivity analytics, and baseline early-risk signals.

It operates on real structured task data and must handle missing or unavailable information safely.

## 2. Input Interface

The module consumes task records following the Shared Structured JSON / Data Contract documented in PROJECT.md. The contract is now present on this branch through the merge from origin/main.

### 2.1 Input Fields

| Field | Requirement | Purpose |
|---|---|---|
| `task_id` | Nullable | Identifies the stored task when an ID has been assigned. |
| `task_title` | Required field; value may be unavailable | Identifies the task or activity. |
| `description` | Optional | Provides additional task details. |
| `task_type` | Required field; value may be unavailable | Identifies the category, such as assignment, exam, quiz, or event. |
| `subject` | Optional | Groups tasks by subject or course. |
| `due_date` | Optional | Preserves the date extracted from the source. |
| `due_time` | Optional | Preserves the time extracted from the source. |
| `due_datetime` | Optional | Provides the normalized deadline for deadline-based calculations. |
| `event_datetime` | Optional | Provides the scheduled time of an event, separately from a submission deadline. |
| `status` | Required; default is `pending` | Provides the authoritative task status from storage. |
| `importance` | Optional | Supplies an explicitly stated or otherwise established importance level, when available. |
| `estimated_effort` | Optional | Supplies the estimated duration or effort, when available. |
| `created_at` | Nullable | Supports task-history and productivity calculations. |
| `completed_at` | Nullable | Supports completion and productivity calculations. |

Other shared contract fields, including `source`, `raw_text`, `date_time_expression`, `confidence`, and `change_information`, remain available in the stored record. Their use will depend on the specific intelligence feature.

## 3. Input Handling Rules

1. The module must accept the shared task structure without renaming its fields.
2. Missing or unknown values must not be invented.
3. `due_datetime` is the primary normalized deadline field for deadline-based calculations. If it is unavailable, the module must not assume a deadline.
4. `event_datetime` represents an event's scheduled time and must not automatically be treated as a submission deadline.
5. `status` must come from the authoritative task/storage layer. The intelligence module must not independently mark a task completed or overdue.
6. `importance` and `estimated_effort` may be unavailable. The module must handle their absence without failing.
7. If estimated effort is missing, workload calculations must not treat the missing value as zero effort.
8. Calculations must distinguish unavailable data from a genuine zero value.

## 4. Output Interface

The module produces three categories of output.

### 4.1 Priority Recommendation

For each task, the module produces:

| Output field | Type | Description |
|---|---|---|
| `task_id` | Integer, string, or null | Links the recommendation to the corresponding task. |
| `priority_score` | Numeric | Represents the task's calculated priority. |
| `priority_label` | String | Communicates the priority category. |
| `priority_reason` | String | Explains the main factors contributing to the recommendation. |

The priority calculation may consider deadline proximity, task type, explicitly available importance, and other agreed signals.

**Proposed design decision for team review:** use a score from 0 to 100 and priority labels `High`, `Medium`, and `Low`. The exact scoring formula and label thresholds must be defined before implementation.

If insufficient information is available, the module must avoid presenting an unsupported recommendation as certain.

### 4.2 Workload and Productivity Analytics

The module produces workload and productivity metrics derived from stored task records.

Potential outputs include:

- Total number of tasks.
- Pending and completed task counts.
- Tasks grouped by subject or task type.
- Upcoming deadlines.
- Known estimated effort, where available.
- Completion trends based on available task history.

Metrics must clearly distinguish complete counts from estimates or partial data. Unknown effort must not be silently counted as zero.

### 4.3 Early-Risk Signals

The initial risk-detection implementation will be a baseline rather than an advanced predictive model.

Potential signals include:

- A pending task with an approaching deadline.
- A pending task whose deadline has passed, based on a valid deadline and the current time.
- Multiple pending tasks with deadlines close together.
- A task or workload pattern that may require attention.

Risk signals must include a reason and reference the relevant task or workload information where possible. Missing deadlines or insufficient history must not be treated as proof of risk.

## 5. Separation of Responsibilities

- **NLP:** extracts task information from messages, notices, and OCR text.
- **Task/storage layer:** assigns task IDs, normalizes deadlines, and maintains authoritative task status and timestamps.
- **Intelligence module:** calculates priority recommendations, workload metrics, productivity metrics, and baseline risk signals.
- **Frontend/dashboard:** displays the intelligence outputs to the student.

The Intelligence module must not overwrite the original extracted information or take ownership of task storage.

## 6. Implementation Scope

The initial implementation will focus on:

1. Priority recommendation.
2. Workload calculation.
3. Productivity analytics.
4. Baseline early-risk detection.

The initial implementation should use real structured task records conforming to the shared contract. Sophisticated personalized intelligence and advanced predictive modelling are outside the initial baseline.

## 7. Open Decisions

The following items require confirmation before or during implementation:

- The final priority-scoring formula and label thresholds.
- The exact format for aggregated workload and productivity outputs.
- The final structure of risk-signal objects.
- How explicitly stated importance and any intelligence-derived importance should interact.
- Which time zone and current-time reference the application will use for deadline and overdue calculations.
- Which fields and history records the database will provide for each analytics calculation.

## 8. Priority Scoring Baseline

### 8.1 Purpose

The initial priority recommendation will use a transparent, rule-based scoring method. It is a baseline for the first implementation, not a trained or validated predictive model.

### 8.2 Input Signals

The scoring method may use:

- **Deadline urgency:** calculated from `due_datetime` and the current time.
- **Importance:** based on an explicitly provided `importance` value, using a documented mapping of accepted values.
- **Task type:** based on a documented, configurable mapping of task types to priority contributions.

`status` will be used to distinguish pending tasks from completed tasks. Completed tasks should not receive active pending-task recommendations.

`estimated_effort` will initially be used for workload calculations. It will not automatically increase a task's priority.

### 8.3 Missing and Invalid Values

- Missing or invalid deadlines must not be treated as known deadlines.
- Missing importance must not be assigned an invented importance value.
- Unknown task types must not receive an invented type-based contribution.
- The calculation must use only valid, available signals and document which signals were unavailable.
- If no usable priority signals are available, the module must return an unavailable score and explain why.
- Missing effort must remain distinct from zero effort.

### 8.4 Outputs

For each eligible task, the module will produce:

- `task_id`
- `priority_score`
- `priority_label`
- `priority_reason`

The score is intended to range from 0 to 100. The formula, signal weights, importance mapping, task-type mapping, and label thresholds must be defined explicitly before implementation and tested against available structured task records.

### 8.5 Validation

The baseline must be tested for approaching deadlines, distant deadlines, past deadlines, completed tasks, missing fields, invalid values, and tasks with insufficient information. The results must not be described as validated predictive performance unless supported by appropriate evaluation.

### 8.6 Deadline Urgency Mapping

The initial deadline urgency score will use the following rules:

| Deadline condition | Urgency score |
|---|---:|
| Overdue and still pending | 100 |
| Due within 24 hours | 95 |
| Due in more than 24 hours and up to 3 days | 75 |
| Due in more than 3 days and up to 7 days | 50 |
| Due in more than 7 days | 25 |
| No valid deadline | Unavailable |

Rules:
- Calculate urgency using `due_datetime` and the current time.
- Apply the overdue score only to tasks whose authoritative status indicates they are still pending.
- Do not infer or change a task's status from its deadline.
- A missing or invalid deadline must not receive an invented urgency score.
- These scores are initial heuristic assumptions and must be evaluated against real structured task records.

### 8.7 Importance Mapping

The initial importance score will use explicitly provided importance values only.

| Importance value | Importance score |
|---|---:|
| High | 100 |
| Medium | 60 |
| Low | 30 |
| Missing or unrecognized | Unavailable |

Rules:
- Match string values case-insensitively after trimming surrounding whitespace.
- Do not infer importance from a task's title, deadline, or type.
- Do not assume a numeric importance scale until its meaning and accepted range are explicitly defined.
- Missing or unrecognized values must not be silently assigned a default score.
- These mappings are initial heuristic assumptions and must be evaluated against available structured task records.

### 8.8 Task-Type Mapping

The initial task-type score will use a configurable mapping:

| Task type | Type score |
|---|---:|
| Exam | 100 |
| Assignment | 80 |
| Quiz | 65 |
| Project | 80 |
| Other or unknown | Unavailable |

Rules:
- Match recognized task-type strings case-insensitively after trimming surrounding whitespace.
- Configure mappings so that additional task types can be added without changing the scoring algorithm.
- Do not infer a task type when it is missing or unrecognized.
- These scores are initial heuristic assumptions and must be reviewed against actual project requirements and structured task records.

### 8.9 Combining Priority Signals

The initial priority score will combine the available signals using these baseline weights:

| Signal | Weight |
|---|---:|
| Deadline urgency | 50% |
| Explicit importance | 30% |
| Task type | 20% |

Rules:
- Use only signals with valid, available scores.
- Normalize the weights of available signals so their combined contribution totals 100%.
- Do not treat an unavailable signal as zero.
- If no signals are available, return an unavailable priority score and explain why.
- Keep the final score within the range 0–100.
- These weights are initial heuristic assumptions and must be evaluated against real structured task records.

### 8.10 Priority Label Thresholds

The initial priority label will be assigned from the final priority score:

| Final priority score | Priority label |
|---|---|
| 70–100 | High |
| 40–69.99 | Medium |
| 0–39.99 | Low |
| Unavailable | Unavailable |

Rules:
- Apply labels only after calculating the final score.
- An unavailable score must produce an Unavailable label, not Low.
- Keep the score within the range 0–100.
- These thresholds are initial heuristic assumptions and must be evaluated against real structured task records.
