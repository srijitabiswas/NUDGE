# Independent NLP Evaluation Benchmark Report (Step 66)

**Execution Timestamp:** 2026-11-03 23:42:47
**Parser Source Branch:** `feature/prakriti-nlp`
**Parser Source Commit:** `01553c92806683731ff68ff4b3513d0c77def9f7`
**Evaluator Location:** `evaluations/evaluate_nlp.py`
**Dataset Source:** `evaluations/nlp_evaluation_dataset.json`

---

## 1. Executive Summary

| Benchmark Scope | Total Cases | Passed | Accuracy / Pass Rate | Result Status |
|---|:---:|:---:|:---:|:---:|
| **Active NLP Extraction Benchmark (12 Fields)** | 40 | 40 | 100.0% | **PASS** |
| **Database Ingestion & Pre-Validation Audit** | 40 | 40 | 100.0% | **PASS** |
| **Deferred Roadmap Diagnostic Cases** | 10 | N/A | Informational | **DOCUMENTED** |

> [!NOTE]
> NLP extraction accuracy and database compatibility checks are evaluated independently. Database ingestion failures never degrade the NLP field extraction score.

---

## 2. Active NLP Extraction Benchmark Results (40 Cases)

### A. Field-by-Field Extraction Accuracy

| Field Name | Total Tested | Exactly Matched | Accuracy | Contract Definition |
|---|:---:|:---:|:---:|---|
| `task_title` | 40 | 40 | 100.0% | 12-field shared contract |
| `description` | 40 | 40 | 100.0% | 12-field shared contract |
| `task_type` | 40 | 40 | 100.0% | 12-field shared contract |
| `subject` | 40 | 40 | 100.0% | 12-field shared contract |
| `due_date` | 40 | 40 | 100.0% | 12-field shared contract |
| `due_time` | 40 | 40 | 100.0% | 12-field shared contract |
| `event_datetime` | 40 | 40 | 100.0% | 12-field shared contract |
| `source` | 40 | 40 | 100.0% | 12-field shared contract |
| `raw_text` | 40 | 40 | 100.0% | 12-field shared contract |
| `date_time_expression` | 40 | 40 | 100.0% | 12-field shared contract |
| `confidence` | 40 | 40 | 100.0% | 12-field shared contract |
| `change_information` | 40 | 40 | 100.0% | 12-field shared contract |

### B. Category Classification Metrics

| Category | Support (True Count) | Precision | Recall | F1-Score |
|---|:---:|:---:|:---:|:---:|
| `task` | 22 | 1.0000 | 1.0000 | **1.0000** |
| `event` | 12 | 1.0000 | 1.0000 | **1.0000** |
| `general_notice` | 6 | 1.0000 | 1.0000 | **1.0000** |

#### Category Confusion Matrix

| Actual \ Predicted | `task` | `event` | `general_notice` |
|---|:---:|:---:|:---:|
| **`task`** | 22 | 0 | 0 |
| **`event`** | 0 | 12 | 0 |
| **`general_notice`** | 0 | 0 | 6 |

### C. Active Suite Discrepancies

**Zero discrepancies found.** 100% of the 40 active benchmark cases passed all 12 field exact-match and category checks.

---

## 3. Database Ingestion & Pre-Validation Audit

Evaluates direct compatibility with `backend.database.repository.insert_task()` using an isolated SQLite database:

- **Total Cases Tested:** 40
- **Successfully Inserted Tasks:** 34
- **Correctly Rejected Records:** 6
- **Total Compatibility Checks Passed:** 40 / 40 (100.0%)
- **General Notice Defense:** All non-task records with `task_title=None` or `task_type=None` were correctly rejected by `insert_task()` raising `ValueError`.

### Database Compatibility Conclusion

PASS: Every valid task record inserted cleanly into SQLite without schema constraint violations, and every general notice was cleanly rejected prior to corrupting the task table.

---

## 4. Deferred Roadmap Diagnostic Analysis (10 Cases)

The 10 deferred cases track parser behavior on pending roadmap steps (Steps 38-39 relative date/time expressions and Steps 41-42 change tracking):

| Case ID | Target Step | Raw Message Snippet | Category | Due Date | Due Time | Event DateTime | Change Information | Status |
|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| `DEF-NLP-01` | Step 38-39 | `Submit the compiler lab writeup in 2 days at ...` | `task` | `None` | `17:00` | `None` | Empty | Pending Step 38-39 |
| `DEF-NLP-02` | Step 38-39 | `Please upload the project report by midnight ...` | `task` | `2026-11-04` | `None` | `None` | Empty | Pending Step 38-39 |
| `DEF-NLP-03` | Step 38-39 | `Reminder: Submit the Networks assignment next...` | `task` | `2026-11-06` | `17:00` | `None` | Empty | Pending Step 38-39 |
| `DEF-NLP-04` | Step 38-39 | `Submit the assignment by 15/11/2026 at 18:00.` | `task` | `None` | `18:00` | `None` | Empty | Pending Step 38-39 |
| `DEF-NLP-05` | Step 38-39 | `Complete the assignment this weekend by Sunda...` | `task` | `2026-11-08` | `None` | `None` | Empty | Pending Step 38-39 |
| `DEF-NLP-06` | Step 38-39 | `Guest lecture on Artificial Intelligence next...` | `event` | `None` | `None` | `None` | Empty | Pending Step 38-39 |
| `DEF-NLP-07` | Step 41-42 | `The Machine Learning assignment deadline has ...` | `task` | `2026-11-15` | `17:00` | `None` | Empty | Pending Step 41-42 |
| `DEF-NLP-08` | Step 41-42 | `Update: Operating Systems exam rescheduled fr...` | `event` | `None` | `None` | `2026-11-20T14:00:00` | Empty | Pending Step 41-42 |
| `DEF-NLP-09` | Step 41-42 | `Notice of change: Project proposal submission...` | `general_notice` | `None` | `None` | `None` | Empty | Pending Step 41-42 |
| `DEF-NLP-10` | Step 41-42 | `Class venue change: Database lecture moved fr...` | `event` | `None` | `None` | `2026-11-12T11:00:00` | Empty | Pending Step 41-42 |

### Roadmap Observations:
1. **Relative date expressions (Steps 38-39):** The parser does not resolve 'in 2 days' or 'next week on Wednesday' in these cases. It does resolve 'next Friday' to 2026-11-06 and 'this weekend by Sunday night' to 2026-11-08, but does not extract the associated night time.
2. **Midnight/time extraction:** 'midnight tonight' produces due_date 2026-11-04 but no due_time. This is partial date extraction, not complete deadline extraction.
3. **Numeric dates:** The DD/MM/YYYY date in DEF-NLP-04 is not extracted, although its time 18:00 is extracted. Slash-date interpretation remains a parsing gap.
4. **Change tracking (Steps 41-42):** All 10 deferred cases return empty change_information. Some rescheduling cases extract a new date or event datetime, but the old/new change is not represented structurally.

---

## 5. Acceptance Checklist for Step 66

- [x] Independent dataset with 50 newly authored cases (40 active + 10 deferred).
- [x] All 12 shared contract fields explicitly asserted and validated.
- [x] Channels strictly conform to `docs/NLP_INTERFACE.md` (`LMS`, `WhatsApp`, `Email`, `Notice`, `Screenshot/OCR`).
- [x] Real-world OCR noisy text patterns simulated and verified.
- [x] General notices correctly leave non-applicable extraction fields unset and return `confidence = 0.0`.
- [x] Database pre-validation verified via isolated SQLite execution.
- [x] Standalone, decoupled evaluator with `--parser-path` CLI option.
