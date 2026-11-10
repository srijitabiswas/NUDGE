# NUDGE Priority Evaluation Cases — Step 68

## Purpose
Define deterministic evaluation cases for the NUDGE rule-based priority recommendation baseline.

## Dataset
The companion `priority_evaluation_dataset.json` contains **31 newly authored cases**.

- P01–P19: Deadline, scoring, importance, task-type and missing-data cases.
- P20: Overdue `in_progress` task with no other valid signals.
- P21: Completed task exclusion.
- P22: Cancelled task exclusion.
- P23: Event task with `event_datetime` only.
- LB01–LB04: Priority-label boundary cases.
  These directly test `get_priority_label()` and assert the label, not a generated priority score.
- FT01-FT04: Full-task threshold-neighbour cases.

Repository search did not locate an existing original 23-case evaluation list. These are newly derived cases, not claimed to be Sresthita's original cases.

## Confirmed scoring rules
- Deadline urgency: overdue = 100; <=24 hours = 95; <=72 hours = 75; <=168 hours = 50; >168 hours = 25.
- Weights: deadline 50%, importance 30%, task type 20%.
- Available signal weights are normalized.
- High >=70; Medium >=40 and <70; Low <40; Unavailable when no valid signals exist.

## Special requirements
- P20: An overdue `in_progress` task without other valid signals must return Unavailable.
- Completed and cancelled tasks must be excluded from active recommendations.
- `event_datetime` must not be treated as a submission deadline.
- Task type `event` remains unscored.

## Known implementation gap
The inspected engine excludes completed tasks but does not explicitly exclude cancelled tasks. P22 records this known implementation gap.

## Timezone handling
The shared contract assigns datetime normalization and timezone handling to the task/storage layer. The inspected engine rejects mixed aware/naive datetime comparisons. No product-wide timezone convention is assumed. The dataset uses consistent naive datetime fixtures for deterministic testing.

## Expected results and execution
Expected scores and labels are specification-derived and arithmetically checked. A scratch evaluation was run against a local copy of the fetched teammate engine branch. The results are recorded below; this does not replace the formal evaluation work planned for later steps.

## Scope
This artifact defines Step 68 evaluation cases only. It does not modify Sresthita's engine or claim predictive accuracy.

## Verified scratch execution

Dataset: 31 cases (P01-P23, LB01-LB04, FT01-FT04).

Execution result:
- **30 PASS**
- **1 KNOWN GAP:** P22 (cancelled task is not explicitly excluded by the inspected engine)
- **0 unexpected failures**
- **31 total cases**

All 30 non-gap cases passed. P22 is deliberately recorded as a known implementation gap, not counted as a pass. The evaluator completed with no unexpected failures.

Engine source: fetched `origin/feature/sresthita-ml`.
Engine commit at report-update time: `03d9ce0ff89d1d242208d9ce8adf3cf2edccb355`

This was a scratch verification of the Step 68 cases. It does not claim that the cancelled-task gap has been fixed or that the later formal evaluation steps are complete.
