"""Tests for change detection, roadmap Step 41.

Run from the repository root:

    python -m unittest nlp.test_step41_change_detection -v

Step 41 decides WHETHER a message announces a change and WHAT kind of change it
is (deadline, date, time, location or other). The old and new values are
Step 42 (see nlp/test_step42_change_values.py), so nothing here checks them.

Kinds: a task whose schedule changed is a "deadline" change; an event whose
schedule changed is a "date" and/or a "time" change; a moved venue is a
"location" change. A message with no change gives [] (never null).
"""

import unittest
from datetime import datetime

from nlp.parser import classify_message_category, parse_message

REF = datetime(2026, 11, 4)  # Wednesday


def parse(text):
    return parse_message(text, "Chat", REF)


def kinds(text):
    return [c["change_type"] for c in parse(text)["change_information"]]


class DetectionTests(unittest.TestCase):
    def test_a_deadline_that_moved(self):
        text = "The Machine Learning assignment deadline has been postponed from 10 November to 15 November at 5 PM."
        self.assertEqual(kinds(text), ["deadline"])
        self.assertEqual(parse(text)["due_date"], "2026-11-15")

    def test_an_exam_that_moved_in_date_and_time(self):
        text = "Update: Operating Systems exam rescheduled from 18 November 10 AM to 20 November 2 PM in Hall C."
        self.assertEqual(kinds(text), ["date", "time"])
        self.assertEqual(parse(text)["event_datetime"], "2026-11-20T14:00:00")

    def test_only_the_time_changed(self):
        text = "The Computer Architecture quiz originally at 10 AM moved to 12 PM on 11 November."
        self.assertEqual(kinds(text), ["time"])

    def test_only_the_date_changed(self):
        text = "The Computer Architecture quiz originally planned for 9 November is now rescheduled to 11 November 2026 at 12 PM."
        self.assertEqual(kinds(text), ["date"])

    def test_a_postponement_with_a_new_date_only(self):
        text = "The Operating Systems mid-sem exam has been postponed to 3rd November, 2 PM."
        self.assertEqual(kinds(text), ["date"])

    def test_a_postponement_with_no_new_date(self):
        self.assertEqual(kinds("The DBMS exam has been postponed."), ["date"])

    def test_a_moved_venue_is_a_location_change(self):
        text = "Class venue change: Database lecture moved from Room 201 to Auditorium on 12 November at 11 AM."
        self.assertEqual(kinds(text), ["location"])
        self.assertEqual(parse(text)["event_datetime"], "2026-11-12T11:00:00")

    def test_a_deadline_extension(self):
        self.assertEqual(kinds("Submit the lab report. Deadline extended to 20 November."), ["deadline"])

    def test_every_entry_has_the_four_contract_keys(self):
        entry = parse("Quiz rescheduled to Friday at 3 PM")["change_information"][0]
        self.assertEqual(set(entry), {"is_changed", "change_type", "old_value", "new_value"})
        self.assertIs(entry["is_changed"], True)
        self.assertIn(entry["change_type"], {"deadline", "date", "time", "location", "other"})


class ChangeNoticeIsATaskTests(unittest.TestCase):
    def test_a_changed_submission_without_an_action_verb_is_a_task(self):
        text = "Notice of change: Project proposal submission moved from Friday 5 PM to Monday 5 PM."
        r = parse(text)
        self.assertEqual(classify_message_category(text, REF), "task")
        self.assertEqual(r["due_date"], "2026-11-09")
        self.assertEqual(r["due_time"], "17:00")
        self.assertEqual(kinds(text), ["deadline"])
        self.assertEqual(r["task_title"], "Project proposal submission moved")

    def test_a_change_notice_without_a_schedule_stays_a_general_notice(self):
        self.assertEqual(
            classify_message_category("The submission format has changed to PDF.", REF), "general_notice"
        )


class NoChangeTests(unittest.TestCase):
    def test_ordinary_messages_have_no_change(self):
        for text in (
            "Submit the DBMS assignment by 20 November at 5 PM.",
            "DBMS quiz tomorrow at 10 am.",
            "Advanced Algorithms lecture on Monday at 10 AM",
            "Please reschedule the meeting for Monday",
            "I changed my phone number, submit the form by Friday",
            "Guest lecture on AI next week on Wednesday at 10 AM",
        ):
            with self.subTest(text=text):
                self.assertEqual(parse(text)["change_information"], [])

    def test_a_notice_that_is_not_a_task_or_event_has_no_entry(self):
        r = parse("The library will remain closed on 2 November.")
        self.assertEqual(r["change_information"], [])

    def test_empty_text(self):
        self.assertEqual(parse("")["change_information"], [])

    def test_the_list_is_not_shared_between_calls(self):
        first = parse("Quiz rescheduled to Friday at 3 PM")
        first["change_information"].append({"x": 1})
        self.assertEqual(len(parse("Quiz rescheduled to Friday at 3 PM")["change_information"]), 1)


class UnchangedFieldsTests(unittest.TestCase):
    def test_other_fields_keep_their_values(self):
        r = parse("The Computer Architecture quiz originally planned for 9 November is now rescheduled to 11 November 2026 at 12 PM.")
        self.assertEqual(r["task_title"], "Computer Architecture quiz rescheduled")
        self.assertEqual(r["event_datetime"], "2026-11-11T12:00:00")
        self.assertEqual(set(r), set(parse("hello")))

    def test_the_raw_text_is_kept(self):
        text = "Quiz rescheduled to Friday at 3 PM"
        self.assertEqual(parse(text)["raw_text"], text)


if __name__ == "__main__":
    unittest.main()
