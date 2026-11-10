"""Save real NLP and OCR-adapter outputs as snapshots (roadmap Step 46).

This script RUNS Prakriti's code, so it needs spaCy. Run it from a throwaway
virtual environment with a copy of her `nlp` folder. The saved JSON files can
then be loaded into the database by backend/database/build_database.py
without needing spaCy.

Example:
    python make_snapshots.py --nlp-dir C:\\temp\\prakriti_nlp ^
        --dataset C:\\temp\\step21.json ^
        --ocr-dir C:\\temp\\prakriti_nlp\\nlp\\test_data\\ocr_samples ^
        --out-dir data\\samples\\real ^
        --parser-commit 6c10f1c07f9b1063f86e29f70396a899cc97c05c

Nothing is guessed: each record stores exactly what the parser returned. The
category comes from classify_message_category and is saved next to the task.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path


def write_json(path, payload):
    Path(path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nlp-dir", required=True, help="folder that contains the 'nlp' package")
    parser.add_argument("--dataset", required=True, help="step21_dataset.json")
    parser.add_argument("--ocr-dir", required=True, help="folder of OCR JSON files")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--parser-commit", required=True, help="Git commit of Prakriti's code")
    parser.add_argument("--ocr-reference-date", default=None,
                        help="YYYY-MM-DD for the OCR files (default: the dataset's reference date)")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(args.nlp_dir).resolve()))
    from nlp.parser import classify_message_category, parse_message
    from nlp.ocr_adapter import parse_ocr_file

    dataset = json.loads(Path(args.dataset).read_text(encoding="utf-8-sig"))
    dataset_ref = dataset["reference_date"]
    ocr_ref = args.ocr_reference_date or dataset_ref
    today = date.today().isoformat()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for case in dataset["cases"]:
        ref = date.fromisoformat(dataset_ref)
        task = parse_message(case["raw_message"], case["source"], ref)
        category = classify_message_category(case["raw_message"], ref)
        records.append({
            "case_id": case["case_id"],
            "source": case["source"],
            "raw_message": case["raw_message"],
            "expected_category": case["expected_category"],
            "category": category,
            "task": task,
        })
    write_json(out_dir / "parser_snapshot.json", {
        "_meta": {
            "description": "Real parse_message output for the Step 21 dataset.",
            "parser_commit": args.parser_commit,
            "generated_on": today,
            "dataset": "nlp/test_data/step21_dataset.json",
            "reference_date": dataset_ref,
            "record_count": len(records),
        },
        "records": records,
    })

    ocr_records = []
    for path in sorted(Path(args.ocr_dir).glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
        ref = date.fromisoformat(ocr_ref)
        result = parse_ocr_file(str(path), reference_date=ref)
        category = classify_message_category(raw.get("cleaned_text") or "", ref)
        ocr_records.append({
            "image": raw.get("source", path.name),
            "category": category,
            "task": result["task"],
            "ocr": result["ocr"],
        })
    write_json(out_dir / "ocr_snapshot.json", {
        "_meta": {
            "description": "Real parse_ocr_file output for the archived OCR JSON files.",
            "parser_commit": args.parser_commit,
            "generated_on": today,
            "ocr_samples": "nlp/test_data/ocr_samples",
            "reference_date": ocr_ref,
            "reference_date_note": "Same as the Step 21 dataset unless given explicitly. "
                                   "The screenshots have no stated reference date.",
            "record_count": len(ocr_records),
        },
        "records": ocr_records,
    })
    print(f"Saved {len(records)} message records and {len(ocr_records)} OCR records to {out_dir}")


if __name__ == "__main__":
    main()
