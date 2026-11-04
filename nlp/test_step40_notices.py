"""Tests for notice and poster text, roadmap Step 40.

Run from the repository root:

    python -m unittest nlp.test_step40_notices -v

Two groups:
  * the nine real OCR samples, checked against the labels in
    nlp/test_data/ocr_samples_expected.json;
  * "held-out" messages written for this step that are NOT taken from the
    nine screenshots, so the rules cannot be memorising them.

Every test uses a fixed reference date (Wednesday 28 October 2026).
"""

import json
import unittest
from datetime import datetime
from pathlib import Path

from nlp import parser
from nlp.ocr_adapter import parse_ocr_file
from nlp.parser import classify_message_category, extract_date, extract_time, parse_message

DATA = Path(__file__).with_name("test_data")
SAMPLES = DATA / "ocr_samples"
REF = datetime(2026, 10, 28)

with open(DATA / "ocr_samples_expected.json", encoding="utf-8") as handle:
    LABELS = json.load(handle)["labels"]


def parse(text):
    return parse_message(text, "Screenshot/OCR", REF)


class OCRSampleLabelTests(unittest.TestCase):
    def test_every_sample_has_a_label(self):
        self.assertEqual(sorted(LABELS), sorted(p.name for p in SAMPLES.glob("*.json")))

    def test_samples_match_their_labels(self):
        for name, label in LABELS.items():
            with self.subTest(sample=name):
                result = parse_ocr_file(SAMPLES / name, REF)["task"]
                category = classify_message_category(result["raw_text"], REF)
                self.assertEqual(category, label["category"])
                for field in ("task_type", "due_date", "due_time", "event_datetime"):
                    self.assertEqual(result[field], label[field], field)
                if "task_title" in label:
                    self.assertEqual(result["task_title"], label["task_title"])
                if "title_contains" in label:
                    self.assertIn(label["title_contains"], result["task_title"])
                if "expression_contains" in label:
                    self.assertIn(label["expression_contains"], result["date_time_expression"])
                for piece in label.get("description_contains", []):
                    self.assertIn(piece, result["description"])

    def test_the_ocr_text_is_never_changed(self):
        for path in SAMPLES.glob("*.json"):
            with self.subTest(sample=path.name):
                with open(path, encoding="utf-8") as handle:
                    record = json.load(handle)
                result = parse_ocr_file(path, REF)["task"]
                self.assertEqual(result["raw_text"], record["cleaned_text"])

    def test_two_dates_leave_the_date_empty_but_are_kept(self):
        result = parse_ocr_file(SAMPLES / "screenshot 3.json", REF)["task"]
        self.assertIsNone(result["event_datetime"])
        self.assertIn("Tuesday, October 27th, 2026", result["description"])
        self.assertIn("Friday, October 30th, 2026", result["description"])


class TimeFormatTests(unittest.TestCase):
    def test_dotted_and_dotted_meridiem_times(self):
        self.assertEqual(extract_time("starts at 8.00 PM"), "20:00")
        self.assertEqual(extract_time("Reporting FN 09.00 a.m."), "09:00")
        self.assertEqual(extract_time("at 2.30 p.m."), "14:30")

    def test_a_range_sharing_one_am_pm_starts_at_the_first_time(self):
        self.assertEqual(extract_time("4.30-5.30 PM"), "16:30")
        self.assertEqual(extract_time("4:30-5:30 PM"), "16:30")
        self.assertEqual(extract_time("11.00-1.00 PM"), "11:00")
        self.assertEqual(extract_time("10:00-12:00 PM"), "10:00")

    def test_earlier_formats_still_work(self):
        self.assertEqual(extract_time("at 2:30 pm"), "14:30")
        self.assertEqual(extract_time("from 10 AM to 12 PM"), "10:00")
        self.assertEqual(extract_time("moved from 3 PM to 5 PM"), "17:00")
        self.assertEqual(extract_time("at 14:45"), "14:45")

    def test_table_noise_is_not_a_time(self):
        self.assertIsNone(extract_time("04-04-2019 9.00.00 AM VENUE"))

    def test_a_time_after_a_month_is_not_a_day(self):
        self.assertIsNone(extract_date("June\n4.30-5.30 PM", REF))
        self.assertEqual(extract_date("5 June 4.30 PM", REF), "2026-06-05")


class DateRangeTests(unittest.TestCase):
    def test_a_range_of_days_uses_the_first_day(self):
        r = parse_message("Viva voce on 10th and 11th December 2026 at 9:00 AM", "Chat", REF)
        self.assertEqual(r["event_datetime"], "2026-12-10T09:00:00")
        self.assertIn("10th and 11th December 2026", r["date_time_expression"])

    def test_a_change_is_not_read_as_a_range(self):
        r = parse_message("Quiz moved from 8 to 12 November", "Chat", REF)
        self.assertEqual(extract_date("Quiz moved from 8 to 12 November", REF), "2026-11-12")
        self.assertIsNone(r["change_information"] or None)


class DeadlineLabelTests(unittest.TestCase):
    def test_last_date_makes_a_task_with_that_date(self):
        r = parse_message("Last date for registration: 30 November 2026", "Chat", REF)
        self.assertEqual(classify_message_category("Last date for registration: 30 November 2026", REF), "task")
        self.assertEqual(r["due_date"], "2026-11-30")

    def test_before_a_date_makes_a_task(self):
        text = "Please pay the library fine before 20 November 2026"
        r = parse_message(text, "Chat", REF)
        self.assertEqual(classify_message_category(text, REF), "task")
        self.assertEqual(r["due_date"], "2026-11-20")
        self.assertEqual(r["task_title"], "Pay the library fine")

    def test_the_labelled_date_beats_other_dates(self):
        text = (
            "NOTICE\nHostel Fee Payment\n"
            "Fee window opens: 2 November 2026\n"
            "Last date for payment: 12 December 2026\n"
            "Late fees apply after that."
        )
        r = parse_message(text, "Notice", REF)
        self.assertEqual(r["due_date"], "2026-12-12")
        self.assertEqual(r["task_title"], "Hostel Fee Payment")

    def test_a_far_away_date_is_not_a_deadline(self):
        # "before" is followed by a date only 70 characters later: not a deadline.
        text = (
            "Fees must be paid before the beginning of the examination which "
            "will be held on 25 November 2026"
        )
        self.assertNotEqual(parse_message(text, "Chat", REF)["due_date"], "2026-11-25")

    def test_a_label_without_a_date_gives_no_date(self):
        text = "LAST DATE TO APPLY:\n677\n0\nTech\nSocial\n9th\n2026"
        self.assertIsNone(parse_message(text, "Notice", REF)["due_date"])


class PosterEventTests(unittest.TestCase):
    def test_invited_talk_with_dotted_time(self):
        text = "AN INVITED TALK ON\nCLOUD SECURITY\nby\nDr A. Sen\n14 November 2026\n6.30 PM\nMode: Online"
        r = parse(text)
        self.assertEqual(classify_message_category(text, REF), "event")
        self.assertEqual(r["task_title"], "Invited talk on Cloud Security")
        self.assertEqual(r["event_datetime"], "2026-11-14T18:30:00")
        self.assertIn("Mode: Online", r["description"])

    def test_a_webinar_with_a_sign_up_button_is_an_event_not_a_task(self):
        text = "Webinar on\nCareer Paths in Data Science\n20 November 2026\n4.30-5.30 PM IST\nRegister Now"
        r = parse(text)
        self.assertEqual(classify_message_category(text, REF), "event")
        self.assertEqual(r["task_title"], "Webinar on Career Paths in Data Science")
        self.assertEqual(r["event_datetime"], "2026-11-20T16:30:00")

    def test_a_distribution_notice_with_two_dates_keeps_both(self):
        text = (
            "NOTICE\nGrade Card Distribution\n"
            "Dates: 3 November 2026 and 5 November 2026\n"
            "Time: 10:00 AM - 1:00 PM\nVenue: Room 12, Admin Block"
        )
        r = parse(text)
        self.assertEqual(classify_message_category(text, REF), "event")
        self.assertEqual(r["task_title"], "Grade Card Distribution")
        self.assertIsNone(r["event_datetime"])
        self.assertIn("3 November 2026", r["description"])
        self.assertIn("5 November 2026", r["description"])
        self.assertIn("Room 12", r["description"])

    def test_a_session_alert_with_no_date_gives_no_date(self):
        text = "SESSION ALERT\nCloud\nComputing\nDATE:\nJANUARY\nTIME:\n7 PM"
        r = parse(text)
        self.assertEqual(r["task_type"], "event")
        self.assertEqual(r["task_title"], "Cloud Computing session")
        self.assertIsNone(r["event_datetime"])
        self.assertIsNone(r["due_date"])
        self.assertEqual(r["date_time_expression"], "7 PM")

    def test_a_poster_with_a_lecture_word_uses_the_existing_rules(self):
        text = "Guest Lecture\nAI in Healthcare\n12 November 2026\n3:30 PM\nSeminar Hall"
        r = parse(text)
        self.assertEqual(r["task_type"], "event")
        self.assertEqual(r["event_datetime"], "2026-11-12T15:30:00")

    def test_a_short_message_is_still_an_event(self):
        r = parse_message("Orientation session on 2 November 2026 at 11 AM", "Chat", REF)
        self.assertEqual(r["event_datetime"], "2026-11-02T11:00:00")
        self.assertEqual(r["task_type"], "event")


class NoticeIsNotATaskTests(unittest.TestCase):
    def test_an_informational_notice_with_a_past_meeting_is_general(self):
        text = (
            "NOTICE\nHonours with Research\n"
            "Eligible students may opt for Honours with Research.\n"
            "The Departmental Council\nMeeting held on 5 August 2026 recommended this.\n"
            "The final award depends on the research publication."
        )
        self.assertEqual(classify_message_category(text, REF), "general_notice")
        self.assertIsNone(parse(text)["task_title"])

    def test_talk_to_is_not_a_talk_event(self):
        text = "Talk to your advisor about the project by 5 November"
        self.assertNotEqual(classify_message_category(text, REF), "event")

    def test_a_word_like_session_without_a_date_is_not_an_event(self):
        self.assertEqual(
            classify_message_category("The session was very useful, thanks", REF), "general_notice"
        )

    def test_register_now_in_a_one_line_message_is_still_a_task(self):
        text = "Register now for the workshop on 10 November 2026"
        self.assertEqual(classify_message_category(text, REF), "task")


class TitleFixTests(unittest.TestCase):
    def test_an_ocr_slip_is_fixed_from_the_same_text(self):
        text = "NOTICE: Payment of Nert Semester Fees\nPay for your next semester by 5 November 2026\nDear Students"
        self.assertEqual(parse(text)["task_title"], "Pay next semester fees")

    def test_nothing_is_changed_when_the_text_gives_no_hint(self):
        text = "NOTICE: Payment of Nert Semester Fees\nPay before 5 November 2026\nDear Students"
        self.assertEqual(parse(text)["task_title"], "Pay nert semester fees")

    def test_raw_text_is_kept_exactly(self):
        text = "NOTICE: Payment of Nert Semester Fees\nPay for your next semester by 5 November 2026\nDear Students"
        self.assertEqual(parse(text)["raw_text"], text)


class UnchangedBehaviourTests(unittest.TestCase):
    def test_next_week_is_still_no_date(self):
        self.assertIsNone(parse_message("Submit the report next week", "Chat", REF)["due_date"])

    def test_change_detection_is_untouched(self):
        r = parse_message("Project deadline moved from 5 November to 8 November for Smart Campus", "Chat", REF)
        self.assertEqual(r["change_information"], [])

    def test_output_keys_are_the_contract_keys(self):
        keys = set(parse_message("hello", "Chat", REF))
        self.assertEqual(set(parse("NOTICE\nPayment of Fees\nLast date: 5 November 2026")), keys)

    def test_an_event_with_only_a_time_keeps_it_in_the_expression(self):
        r = parse_message("Seminar at 4 PM", "Chat", REF)
        self.assertIsNone(r["due_time"])
        self.assertIsNone(r["event_datetime"])
        self.assertEqual(r["date_time_expression"], "4 PM")


if __name__ == "__main__":
    unittest.main()
