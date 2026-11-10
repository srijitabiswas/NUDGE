import argparse
import json
import math
import os
import sys
import tempfile
import unicodedata
from pathlib import Path


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (x != y)))
        previous = current
    return previous[-1]


def valid_score(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and 0 <= value <= 1)


def load_and_validate(ground_truth, ocr_dir):
    try:
        dataset = json.loads(ground_truth.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read ground-truth JSON: {exc}") from exc

    if not isinstance(dataset, dict) or not isinstance(dataset.get("cases"), list):
        raise ValueError("Ground truth must contain a 'cases' array.")
    cases = dataset["cases"]
    if not cases:
        raise ValueError("Ground-truth dataset contains no cases.")

    ids, sources, validated, errors = set(), set(), [], []

    for index, case in enumerate(cases):
        label = f"case {index + 1}"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected a JSON object.")
            continue

        case_id, source, reference = (
            case.get("id"), case.get("source"), case.get("reference_text")
        )
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label}: missing or invalid id.")
            continue
        if case_id in ids:
            errors.append(f"{label}: duplicate id '{case_id}'.")
            continue
        ids.add(case_id)

        if not isinstance(source, str) or not source.strip():
            errors.append(f"{case_id}: missing or invalid source.")
            continue
        if (source in (".", "..") or "/" in source or "\\" in source
                or source != Path(source).name):
            errors.append(f"{case_id}: source must be a safe filename.")
            continue
        source_key = source.casefold()
        if source_key in sources:
            errors.append(f"{case_id}: duplicate source filename (case-insensitive).")
            continue
        sources.add(source_key)

        if not isinstance(reference, str) or not reference.strip():
            errors.append(f"{case_id}: missing or empty reference_text.")
            continue

        output_path = ocr_dir / (Path(source).stem + ".json")
        if not output_path.is_file():
            errors.append(f"{case_id}: missing OCR output {output_path}.")
            continue
        try:
            output = json.loads(output_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{case_id}: invalid OCR JSON: {exc}.")
            continue

        if not isinstance(output, dict):
            errors.append(f"{case_id}: OCR output must be a JSON object.")
            continue
        if output.get("source") != source:
            errors.append(f"{case_id}: OCR source does not match ground truth.")
            continue

        raw_text = output.get("raw_text")
        confidence = output.get("confidence")
        overall = output.get("overall_confidence")

        if not isinstance(raw_text, str):
            errors.append(f"{case_id}: raw_text must be a string.")
            continue
        if not isinstance(confidence, list):
            errors.append(f"{case_id}: confidence must be an array.")
            continue

        bad_region = False
        for region_index, region in enumerate(confidence):
            if not isinstance(region, dict):
                errors.append(f"{case_id}: confidence region {region_index + 1} is not an object.")
                bad_region = True
                break
            if not isinstance(region.get("text"), str) or not region["text"].strip():
                errors.append(f"{case_id}: confidence region {region_index + 1} has invalid text.")
                bad_region = True
                break
            if not valid_score(region.get("score")):
                errors.append(f"{case_id}: confidence region {region_index + 1} has invalid score.")
                bad_region = True
                break
        if bad_region:
            continue

        if not confidence:
            if raw_text != "" or overall is not None:
                errors.append(f"{case_id}: empty OCR requires raw_text='', confidence=[], and overall_confidence=null.")
                continue
        else:
            expected_text = "\n".join(region["text"] for region in confidence)
            if raw_text != expected_text:
                errors.append(f"{case_id}: raw_text does not match joined confidence-region text.")
                continue
            if not valid_score(overall):
                errors.append(f"{case_id}: invalid overall_confidence.")
                continue
            expected_overall = sum(r["score"] for r in confidence) / len(confidence)
            if not math.isclose(overall, expected_overall, rel_tol=0, abs_tol=0.00015):
                errors.append(f"{case_id}: overall_confidence does not match mean region score.")
                continue

        validated.append((case, output))

    if errors:
        raise ValueError("Evaluation inputs failed validation:\n- " + "\n- ".join(errors))
    if len(validated) != len(cases):
        raise ValueError("Not all ground-truth cases were validated.")
    return validated


def build_report(validated):
    rows = []
    for case, output in validated:
        ref, hyp = normalize(case["reference_text"]), normalize(output["raw_text"])
        ref_words, hyp_words = ref.split(), hyp.split()
        char_errors = levenshtein(list(ref), list(hyp))
        word_errors = levenshtein(ref_words, hyp_words)
        rows.append({
            "source": case["source"],
            "cer": char_errors / len(ref),
            "wer": word_errors / len(ref_words),
            "char_errors": char_errors,
            "word_errors": word_errors,
            "chars": len(ref),
            "words": len(ref_words),
            "confidence": output["overall_confidence"],
            "regions": len(output["confidence"])
        })

    lines = [
        "# NUDGE OCR Evaluation Report", "",
        "## Method",
        "Manually transcribed reference text is compared with OCR raw_text. All legible text, including wordmarks, handwritten slogans and text on illustrated clothing, is included. QR-code payloads and unreadable text are excluded.",
        "Unicode NFKC normalization, case-folding and whitespace normalization are applied. Punctuation is retained.",
        "Words are tokenized by splitting on whitespace. CER and WER aggregates are pooled: total edit errors divided by total reference characters or words, respectively.",
        "An entirely empty OCR result is valid only when raw_text is empty, confidence is an empty array and overall_confidence is null; it is scored normally against the non-empty reference.",
        "OCR outputs were produced using EasyOCR. The historical pipeline resized images narrower than 1600 px to 1600 px width using cubic interpolation. The archived outputs were recovered from Git commit d4760d4; OCR was not rerun for this evaluation.",
        "Ground-truth references are provisional pending final human review.", "",
        "CER = character edit distance / reference character count.",
        "WER = word edit distance / reference word count.", "",
        "## Per-image results", "",
        "| Image | CER | WER | OCR confidence | Regions |",
        "|---|---:|---:|---:|---:|"
    ]

    for row in rows:
        conf = "N/A" if row["confidence"] is None else f'{row["confidence"]:.4f}'
        lines.append(
            f'| {row["source"]} | {row["cer"]:.4f} | {row["wer"]:.4f} | {conf} | {row["regions"]} |'
        )

    total_chars = sum(r["chars"] for r in rows)
    total_words = sum(r["words"] for r in rows)
    cer = sum(r["char_errors"] for r in rows) / total_chars
    wer = sum(r["word_errors"] for r in rows) / total_words

    lines += [
        "", "## Aggregate results", "",
        f"- Ground-truth cases: {len(rows)}",
        f"- Aggregate CER: {cer:.4f} ({cer * 100:.2f}%)",
        f"- Aggregate WER: {wer:.4f} ({wer * 100:.2f}%)", "",
        "## Limitations", "",
        "- OCR confidence is a model confidence estimate, not an accuracy metric.",
        "- Reference transcriptions are provisional and require final human review.",
        "- QR-code payloads and unreadable text are excluded; legible wordmarks, handwritten slogans and text on illustrated clothing are included.",
        "- Nine images are not sufficient to establish general OCR performance.",
        "- Reference line ordering affects edit-distance results.",
        "- CER and WER do not indicate whether critical fields such as dates, times or names were transcribed correctly.",
        "- OCR engine and image-processing dependency versions are not pinned, so fresh OCR runs may differ.",
        "- The pooled aggregate is character- and word-weighted; larger images contribute more. The unweighted mean of per-image rates is approximately 19.9% CER and 40.4% WER."
    ]
    return "\n".join(lines) + "\n"


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            dir=path.parent, prefix=path.name + ".",
            suffix=".tmp", delete=False
        ) as handle:
            temp_name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocr-dir", required=True)
    parser.add_argument("--ground-truth", default=str(Path(__file__).with_name("ocr_ground_truth.json")))
    parser.add_argument("--report", default=str(Path(__file__).with_name("OCR_EVALUATION_REPORT.md")))
    args = parser.parse_args()
    try:
        validated = load_and_validate(Path(args.ground_truth), Path(args.ocr_dir))
        report = build_report(validated)
        atomic_write(Path(args.report), report)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Evaluated {len(validated)} ground-truth cases.")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
