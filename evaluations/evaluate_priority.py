import json, sys
from datetime import datetime

sys.path.insert(0, sys.argv[2])
from ml.priority_engine import generate_priority_recommendation, get_priority_label

with open(sys.argv[1], encoding="utf-8-sig") as f:
    data = json.load(f)

rows = []
unexpected = 0

for c in data["cases"]:
    exp = c["expected"]

    if "input" in c:
        got_score = None
        got_label = get_priority_label(c["input"]["priority_score"])
        score_ok = True
    else:
        out = generate_priority_recommendation(
            c["task"], datetime.fromisoformat(c["current_time"])
        )
        got_score = out["priority_score"]
        got_label = out["priority_label"]
        score_ok = got_score == exp["priority_score"]

    label_ok = got_label == exp["priority_label"]
    ok = score_ok and label_ok
    known = c.get("basis") == "confirmed_decision_engine_gap"
    status = "PASS" if ok else ("KNOWN GAP" if known else "FAIL")
    unexpected += int(not ok and not known)

    rows.append((c["case_id"], status, score_ok, label_ok,
                 exp.get("priority_score", "n/a"),
                 exp["priority_label"], got_score, got_label))

for r in rows:
    print(f"{r[0]:5} {r[1]:9} score={'ok' if r[2] else 'MISMATCH':8} label={'ok' if r[3] else 'MISMATCH':8} expected {r[4]} {r[5]} | engine {r[6]} {r[7]}")

print(f"\n{sum(r[1]=='PASS' for r in rows)} pass, {sum(r[1]=='KNOWN GAP' for r in rows)} known gap, {unexpected} unexpected failures, {len(rows)} total")
sys.exit(1 if unexpected else 0)
