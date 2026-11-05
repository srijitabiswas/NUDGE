"""Tests for old and new values of a change, roadmap Step 42.

Run from the repository root:

    python -m unittest nlp.test_step42_change_values -v

Values are the date/time words as the message wrote them ("Friday 5 PM"),
never converted. An old value that the message does not state is null; the
parser has no memory of earlier messages, so it never fills it in.
"""

import unittest
from datetime import datetime

from nlp.parser import parse_message

REF = datetime(2026, 11, 4)  # Wednesday


def changes(text):
    return [
        (c["change_type"], c["old_value"], c["new_value"])
        for c in parse_message(text, "Chat", REF)["change_information"]
    ]


class DeadlineValueTests(unittest.TestCase):
    def test_from_one_date_to_another(self):
        self.assertEqual(
            changes("Update: the Web Technologies project deadline has moved from 8 November to 12 November 2026."),
            [("deadline", "8 November", "12 November 2026")],
        )

    def test_the_new_value_keeps_its_time(self):
        self.assertEqual(
            changes("The Machine Learning assignment deadline has been postponed from 10 November to 15 November at 5 PM."),
            [("deadline", "10 November", "15 November at 5 PM")],
        )

    def test_weekday_values_stay_as_written(self):
        self.assertEqual(
            changes("Notice of change: Project proposal submission moved from Friday 5 PM to Monday 5 PM."),
            [("deadline", "Friday 5 PM", "Monday 5 PM")],
        )

    def test_only_the_new_value_is_known(self):
        self.assertEqual(
            changes("Submit the lab report. Deadline extended to 20 November."),
            [("deadline", None, "20 November")],
        )

    def test_the_old_value_before_the_verb(self):
        self.assertEqual(
            changes("Submit the report. The deadline of 5 November has been extended to 9 November."),
            [("deadline", "5 November", "9 November")],
        )


class DateAndTimeValueTests(unittest.TestCase):
    def test_a_date_and_a_time_that_both_changed_are_two_entries(self):
        self.assertEqual(
            changes("Update: Operating Systems exam rescheduled from 18 November 10 AM to 20 November 2 PM in Hall C."),
            [("date", "18 November", "20 November"), ("time", "10 AM", "2 PM")],
        )

    def test_only_the_time_changed(self):
        self.assertEqual(
            changes("The Computer Architecture quiz originally at 10 AM moved to 12 PM on 11 November."),
            [("time", "10 AM", "12 PM")],
        )

    def test_only_the_date_changed(self):
        self.assertEqual(
            changes("The Computer Architecture quiz originally planned for 9 November is now rescheduled to 11 November 2026 at 12 PM."),
            [("date", "9 November", "11 November 2026")],
        )

    def test_the_same_date_with_a_new_time_is_only_a_time_change(self):
        self.assertEqual(
            changes("Exam rescheduled from 10 November 10 AM to 10 November 2 PM"),
            [("time", "10 AM", "2 PM")],
        )

    def test_only_the_new_date_is_known(self):
        self.assertEqual(
            changes("The Operating Systems mid-sem exam has been postponed to 3rd November, 2 PM."),
            [("date", None, "3rd November")],
        )

    def test_the_new_value_written_first(self):
        self.assertEqual(
            changes("Quiz rescheduled to 12 November from 10 November"),
            [("date", "10 November", "12 November")],
        )

    def test_a_time_range_after_a_new_date_is_not_a_change_of_time(self):
        self.assertEqual(
            changes("Quiz rescheduled to 12 November, from 10 AM to 12 PM"),
            [("date", None, "12 November")],
        )

    def test_a_relative_word_value(self):
        self.assertEqual(
            changes("Seminar rescheduled from tomorrow to Friday"),
            [("date", "tomorrow", "Friday")],
        )

    def test_no_new_value_given(self):
        self.assertEqual(changes("The DBMS exam has been postponed."), [("date", None, None)])


class OtherKindsTests(unittest.TestCase):
    def test_a_location_change_has_no_values_in_step_42(self):
        self.assertEqual(
            changes("Class venue change: Database lecture moved from Room 201 to Auditorium on 12 November at 11 AM."),
            [("location", None, None)],
        )

    def test_no_change_is_an_empty_list(self):
        self.assertEqual(changes("Submit the DBMS assignment by 20 November at 5 PM."), [])


class ConsistencyTests(unittest.TestCase):
    def test_the_top_level_date_is_the_new_one(self):
        r = parse_message(
            "Update: the Web Technologies project deadline has moved from 8 November to 12 November 2026.",
            "Chat", REF,
        )
        self.assertEqual(r["due_date"], "2026-11-12")
        self.assertEqual(r["change_information"][0]["new_value"], "12 November 2026")

    def test_the_entry_has_exactly_the_contract_keys(self):
        entry = parse_message("Quiz rescheduled to Friday at 3 PM", "Chat", REF)["change_information"][0]
        self.assertEqual(set(entry), {"is_changed", "change_type", "old_value", "new_value"})

    def test_values_are_strings_or_null(self):
        for text in (
            "Quiz rescheduled to Friday at 3 PM",
            "Exam rescheduled from 18 November 10 AM to 20 November 2 PM",
            "The DBMS exam has been postponed.",
        ):
            for entry in parse_message(text, "Chat", REF)["change_information"]:
                for key in ("old_value", "new_value"):
                    self.assertTrue(entry[key] is None or isinstance(entry[key], str))

    def test_the_raw_text_is_kept(self):
        text = "Quiz rescheduled to Friday at 3 PM"
        self.assertEqual(parse_message(text, "Chat", REF)["raw_text"], text)


if __name__ == "__main__":
    unittest.main()
