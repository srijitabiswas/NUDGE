"""Tests for nlp/parser.py, roadmap Phase 2 (Steps 14-21).

Run from the repository root:

    python -m unittest discover -s nlp -p "test_*.py" -v

Every test uses a fixed reference date, so the results never depend on the
day the tests are run. Test groups follow the roadmap steps:

    Step 14  basic parsing         Step 18  classification
    Step 15  titles/descriptions   Step 19  missing fields
    Step 16  dates                 Step 20  confidence
    Step 17  times                 Step 21  representative dataset

The "held-out" tests at the end use messages that are NOT in the Step 21
dataset; their expected values were written by the parser's author, following
the dataset's conventions, to check that the parser is not memorising the 25
dataset messages.
"""

import unittest
from datetime import date, datetime
from pathlib import Path

from nlp import evaluate_step21
from nlp.parser import (
    calculate_confidence,
    classify_message_category,
    classify_task_type,
    extract_date,
    extract_description,
    extract_subject,
    extract_task_title,
    extract_time,
    is_event_message,
    is_general_notice,
    parse_message,
)

# A Monday: "tomorrow" is 2026-10-13 and "Friday" is 2026-10-16.
REF = datetime(2026, 10, 12, 9, 0)
PARSER_FILE = Path(__file__).with_name("parser.py")

CONTRACT_KEYS = {
    "task_title", "description", "task_type", "subject", "due_date",
    "due_time", "event_datetime", "source", "raw_text",
    "date_time_expression", "confidence", "change_information",
}


def parse(text, source="Test", reference=REF):
    return parse_message(text, source, reference)


# --------------------------------------------------
# STEP 14: basic message parsing
# --------------------------------------------------

class Step14BasicParsingTests(unittest.TestCase):
    def test_parser_source_has_no_stray_control_characters(self):
        # Commit f50e23d once put two backspace characters (0x08) where "\b"
        # belonged in a regex, so that regex could never match.
        data = PARSER_FILE.read_bytes()
        bad = sorted({b for b in data if b < 0x20 and b not in (0x09, 0x0A, 0x0D)})
        self.assertEqual(bad, [], f"control characters found in parser.py: {bad}")

    def test_project_md_example(self):
        r = parse(
            "Dear Students, please submit your Machine Learning Assignment 1 "
            "on Moodle by 15th October at 5:00 PM.",
            "LMS Notice",
        )
        self.assertEqual(r["task_title"], "Submit Machine Learning Assignment 1")
        self.assertEqual(r["description"], "Submit on Moodle")
        self.assertEqual(r["task_type"], "assignment")
        self.assertEqual(r["subject"], "Machine Learning")
        self.assertEqual(r["due_date"], "2026-10-15")
        self.assertEqual(r["due_time"], "17:00")
        self.assertIsNone(r["event_datetime"])
        self.assertEqual(r["source"], "LMS Notice")
        self.assertEqual(r["date_time_expression"], "15th October at 5:00 PM")
        self.assertEqual(r["change_information"], [])

    def test_output_has_exactly_the_contract_fields(self):
        messages = [
            "Submit the DBMS assignment by 20th October at 5 PM.",   # task
            "DBMS quiz tomorrow at 10 am.",                          # event
            "The library will remain closed on 2 November.",         # notice
            "",                                                      # empty
        ]
        for message in messages:
            with self.subTest(message=message):
                self.assertEqual(set(parse(message)), CONTRACT_KEYS)

    def test_fields_owned_by_the_storage_layer_are_never_produced(self):
        r = parse("Submit the DBMS assignment by 20th October at 5 PM.")
        for owned_elsewhere in ("task_id", "due_datetime", "status", "created_at", "completed_at"):
            self.assertNotIn(owned_elsewhere, r)

    def test_source_and_raw_text_are_returned_unchanged(self):
        raw = "  Submit the DBMS assignment by 20th October.  "
        r = parse(raw, "WhatsApp")
        self.assertEqual(r["raw_text"], raw)
        self.assertEqual(r["source"], "WhatsApp")

    def test_explicit_action_makes_a_task_even_with_an_event_word(self):
        # This is the Step 14 regex bug: "bring" was never recognised.
        r = parse("Bring your ID card for the viva on 5th November at 10 AM.")
        self.assertIsNone(r["event_datetime"])
        self.assertEqual(r["due_date"], "2026-11-05")
        self.assertEqual(r["due_time"], "10:00")
        self.assertEqual(classify_message_category("Bring your ID card for the viva on 5th November at 10 AM."), "task")

    def test_attend_keeps_an_event_an_event(self):
        r = parse("Please attend the workshop on 14 November at 3 PM.")
        self.assertEqual(r["task_type"], "event")
        self.assertEqual(r["event_datetime"], "2026-11-14T15:00:00")
        self.assertIsNone(r["due_date"])

    def test_change_information_list_is_not_shared_between_calls(self):
        first = parse("Submit the DBMS assignment by 20th October.")
        first["change_information"].append({"is_changed": True})
        second = parse("Submit the DBMS assignment by 20th October.")
        self.assertEqual(second["change_information"], [])

    def test_reference_date_can_be_a_date_or_a_datetime(self):
        message = "Submit the DBMS assignment tomorrow."
        self.assertEqual(parse(message, reference=date(2026, 10, 12))["due_date"], "2026-10-13")
        self.assertEqual(parse(message, reference=datetime(2026, 10, 12, 23, 59))["due_date"], "2026-10-13")

    def test_reference_date_of_the_wrong_type_is_rejected_clearly(self):
        with self.assertRaises(TypeError):
            parse("Submit the DBMS assignment tomorrow.", reference="2026-10-12")


# --------------------------------------------------
# STEP 15: titles and descriptions
# --------------------------------------------------

class Step15TitleTests(unittest.TestCase):
    def assertTitle(self, message, expected):
        self.assertEqual(parse(message)["task_title"], expected, message)

    def test_assignment_titles_keep_the_number(self):
        self.assertTitle("Please submit Machine Learning Assignment 2 on Moodle by 5 November 2026 at 5:00 PM.",
                         "Submit Machine Learning Assignment 2")
        self.assertTitle("Reminder: Data Structures assignment is due on 7 November.",
                         "Submit Data Structures assignment")
        self.assertTitle("Machine Learning Assignment 3 is due on 7 November.",
                         "Submit Machine Learning Assignment 3")

    def test_prefixes_are_removed(self):
        self.assertTitle("Reminder: Submit the lab report by 25 October.", "Submit lab report")
        self.assertTitle("Dear Students, please submit the lab report by 25 October.", "Submit lab report")
        self.assertTitle("Kindly submit the lab report by 25 October.", "Submit lab report")

    def test_a_greeting_sentence_is_not_the_title(self):
        self.assertTitle("Hi everyone. Please submit the lab report by 25 October.", "Submit lab report")

    def test_the_when_part_is_removed_but_the_topic_is_kept(self):
        self.assertTitle("Seminar on Artificial Intelligence on 12 November.", "Seminar on Artificial Intelligence")
        self.assertTitle("Statistics quiz on Friday at 2 PM. Room details will follow.", "Statistics quiz")
        self.assertTitle("The Operating Systems mid-semester exam will be held on 10 November 2026 at 10:30 AM.",
                         "Operating Systems mid-semester exam")

    def test_trailing_when_words_are_removed_even_with_a_full_stop(self):
        # Used to work only for one hard-coded sentence.
        self.assertTitle("Reminder: bring your admit card to campus tomorrow.", "Bring admit card to campus")
        self.assertTitle("Reminder: bring your ID card to campus tomorrow.", "Bring ID card to campus")

    def test_only_the_first_clause_is_used(self):
        self.assertTitle("Please attend the workshop, it is already confirmed. Workshop on 14 November at 3 PM.",
                         "Workshop")

    def test_meeting_for_a_topic(self):
        self.assertTitle("Team meeting for the final-year project next Monday at 11 AM.",
                         "Final-year project team meeting")
        self.assertTitle("Review meeting for the Smart Campus project on 3 November at 4 PM.",
                         "Smart Campus project review meeting")
        self.assertTitle("Please attend the project review meeting at 4 PM.", "Project review meeting")

    def test_change_notices_become_change_titles(self):
        self.assertTitle("The Operating Systems mid-sem exam has been postponed to 3rd November, 2 PM.",
                         "Operating Systems mid-sem exam postponed")
        self.assertTitle("The Computer Architecture quiz originally planned for 9 November is now rescheduled "
                         "to 11 November 2026 at 12 PM.", "Computer Architecture quiz rescheduled")
        self.assertTitle("Update: the Web Technologies project deadline has moved from 8 November to "
                         "12 November 2026.", "Web Technologies project deadline change")
        self.assertTitle("Deadline for Network Security lab report extended to 20th November.",
                         "Network Security lab report deadline change")
        self.assertTitle("DBMS assignment deadline moved from 10th October to 15th October.",
                         "DBMS assignment deadline change")
        # The subject is named after the change words, so it is moved to the front.
        self.assertTitle("Project deadline moved to 2nd November for Smart Campus.",
                         "Smart Campus project deadline change")

    def test_passive_instructions_become_action_titles(self):
        self.assertTitle("The internship report must be submitted by Friday at 5 PM.", "Submit internship report")
        self.assertTitle("Project proposal for the Smart Campus project must be uploaded by 12 November 2026.",
                         "Upload Smart Campus project proposal")

    def test_task_with_two_actions_keeps_both(self):
        self.assertTitle("Prepare and submit the Artificial Intelligence mini-project. "
                         "The deadline has not been announced yet.",
                         "Prepare and submit Artificial Intelligence mini-project")

    def test_a_message_that_starts_with_the_date_still_gets_a_title(self):
        self.assertTitle("Tomorrow at 9 AM: DBMS quiz in room 12.", "DBMS quiz in room 12")

    def test_empty_text_has_no_title(self):
        self.assertIsNone(extract_task_title("   "))


class Step15DescriptionTests(unittest.TestCase):
    def test_submission_platform(self):
        self.assertEqual(extract_description("Please submit the report on Moodle by 5 November."),
                         "Submit on Moodle")

    def test_other_platform_for_non_submissions(self):
        self.assertEqual(extract_description("Project meeting on Teams tomorrow at 4 PM."), "On Teams")

    def test_location(self):
        self.assertEqual(extract_description("Class tomorrow at 8 AM in room 204."), "Location: Room 204")
        self.assertEqual(extract_description("Our lecture starts tomorrow at 9:00 AM in Lab 3."), "Location: Lab 3")

    def test_extra_sentences_become_notes(self):
        self.assertEqual(extract_description("Statistics quiz on Friday at 2 PM. Room details will follow."),
                         "Room details will follow")

    def test_notes_that_repeat_the_date_or_greet_are_not_copied(self):
        self.assertIsNone(extract_description("Hi everyone. Workshop on 14 November at 3 PM."))
        self.assertIsNone(extract_description("Please attend the workshop on 14 November at 3 PM."))

    def test_no_description_when_there_is_nothing_to_add(self):
        self.assertIsNone(extract_description("Submit the DBMS assignment by 20th October."))
        self.assertIsNone(parse("Submit the DBMS assignment by 20th October.")["description"])


# --------------------------------------------------
# STEP 16: dates
# --------------------------------------------------

class Step16DateTests(unittest.TestCase):
    def assertDate(self, text, expected, reference=REF):
        self.assertEqual(extract_date(text, reference), expected, text)

    def test_day_month_formats(self):
        self.assertDate("by 20th October", "2026-10-20")
        self.assertDate("by 5 November 2026", "2026-11-05")
        self.assertDate("by 5th of November", "2026-11-05")

    def test_month_day_formats(self):
        self.assertDate("by November 12", "2026-11-12")
        self.assertDate("by November 12, 2027", "2027-11-12")

    def test_abbreviated_months(self):
        self.assertDate("by 5 Nov", "2026-11-05")
        self.assertDate("by 5 Nov.", "2026-11-05")
        self.assertDate("by Sept 9", "2026-09-09")

    def test_iso_format(self):
        self.assertDate("due 2026-11-05", "2026-11-05")

    def test_a_written_year_is_used(self):
        self.assertDate("by 5 November 2027", "2027-11-05")

    def test_a_date_without_a_year_takes_the_nearest_year(self):
        self.assertDate("by 5th January", "2027-01-05", reference=datetime(2026, 12, 20))
        self.assertDate("by 20th December", "2025-12-20", reference=datetime(2026, 1, 5))
        self.assertDate("by 5th October", "2026-10-05")  # slightly in the past: same year

    def test_relative_days(self):
        self.assertDate("by tomorrow", "2026-10-13")
        self.assertDate("due today", "2026-10-12")
        self.assertDate("starts tonight", "2026-10-12")

    def test_weekdays_mean_the_next_occurrence(self):
        self.assertDate("by Friday", "2026-10-16")
        self.assertDate("on Monday", "2026-10-19")   # today is Monday: next week
        self.assertDate("next Monday", "2026-10-19")

    def test_next_week_is_too_vague_for_a_date(self):
        self.assertDate("The fest is next week", None)

    def test_an_explicit_date_beats_a_relative_word(self):
        self.assertDate("Submit by 28th October, please start tomorrow.", "2026-10-28")
        self.assertDate("Submit by 28th October, the fest is next week.", "2026-10-28")

    def test_the_last_date_wins_for_a_change(self):
        self.assertDate("deadline moved from 10th October to 15th October", "2026-10-15")

    def test_impossible_dates_are_not_invented(self):
        self.assertDate("by 31 February", None)
        self.assertDate("by 32 October", None)

    def test_a_time_is_not_read_as_a_date(self):
        self.assertDate("Quiz on 3rd November 2 PM", "2026-11-03")
        self.assertDate("Submit before 7 PM", None)

    def test_no_date_gives_none(self):
        self.assertDate("Submit your assignment soon", None)


# --------------------------------------------------
# STEP 17: times
# --------------------------------------------------

class Step17TimeTests(unittest.TestCase):
    def assertTime(self, text, expected):
        self.assertEqual(extract_time(text), expected, text)

    def test_twelve_hour_with_minutes(self):
        self.assertTime("at 5:00 PM", "17:00")
        self.assertTime("at 10:30 am", "10:30")
        self.assertTime("at 9:05AM", "09:05")

    def test_twelve_hour_without_minutes(self):
        self.assertTime("by 6 PM", "18:00")
        self.assertTime("at 10 am", "10:00")

    def test_noon_and_midnight_hours(self):
        self.assertTime("at 12 PM", "12:00")
        self.assertTime("at 12 AM", "00:00")
        self.assertTime("at noon", "12:00")

    def test_twenty_four_hour_clock(self):
        self.assertTime("at 17:30", "17:30")
        self.assertTime("at 08:15", "08:15")

    def test_a_time_range_uses_the_start_time(self):
        self.assertTime("exam from 10 AM to 12 PM", "10:00")
        self.assertTime("exam 9:30 AM - 11:30 AM", "09:30")

    def test_a_change_uses_the_new_time(self):
        self.assertTime("quiz moved from 3 PM to 5 PM", "17:00")
        self.assertTime("The exam is rescheduled from 10 AM to 2 PM", "14:00")

    def test_the_last_time_wins_otherwise(self):
        self.assertTime("Reporting at 8 AM, submission by 5 PM", "17:00")

    def test_invalid_times_are_not_invented(self):
        self.assertTime("at 13 PM", None)
        self.assertTime("at 13 AM", None)
        self.assertTime("at 0 PM", None)
        self.assertTime("at 10:75 PM", None)

    def test_digits_of_a_date_are_not_a_time(self):
        self.assertTime("by 5 November 2026", None)
        self.assertTime("on 2026-11-05", None)

    def test_no_time_gives_none(self):
        self.assertTime("Submit by Friday", None)


class Step16And17ExpressionTests(unittest.TestCase):
    """date_time_expression keeps the literal date/time words (interface section 7)."""

    def test_date_and_time_together(self):
        self.assertEqual(parse("Submit by 15th October at 5 PM.")["date_time_expression"], "15th October at 5 PM")
        self.assertEqual(parse("Submit by tomorrow at 11:59 PM.")["date_time_expression"], "tomorrow at 11:59 PM")

    def test_time_before_date(self):
        self.assertEqual(parse("Submit your DBMS lab record by 6 PM today.")["date_time_expression"], "6 PM today")

    def test_date_only_and_time_only(self):
        self.assertEqual(parse("Submit the report by 20 November 2026.")["date_time_expression"], "20 November 2026")
        self.assertEqual(parse("Please complete the Discrete Mathematics quiz before 7 PM.")["date_time_expression"], "7 PM")

    def test_a_time_range_is_kept_whole(self):
        r = parse("Operating Systems exam from 10 AM to 12 PM on 5th November.")
        self.assertEqual(r["date_time_expression"], "10 AM to 12 PM on 5th November")
        self.assertEqual(r["event_datetime"], "2026-11-05T10:00:00")

    def test_a_vague_period_is_kept_when_there_is_nothing_more_exact(self):
        r = parse("The college cultural fest will take place next week. More details soon.")
        self.assertEqual(r["date_time_expression"], "next week")
        self.assertIsNone(r["event_datetime"])

    def test_no_expression_when_the_message_has_no_date_or_time(self):
        self.assertIsNone(parse("Submit the DBMS assignment.")["date_time_expression"])

    def test_no_expression_when_the_deadline_is_stated_to_be_unknown(self):
        r = parse("Please submit your assignment soon. The exact deadline will be announced by the instructor.")
        self.assertIsNone(r["date_time_expression"])


# --------------------------------------------------
# STEP 18: classification (type, subject, task vs event vs notice)
# --------------------------------------------------

class Step18ClassificationTests(unittest.TestCase):
    def test_task_types(self):
        cases = {
            "Submit the DBMS assignment": "assignment",
            "Complete the quiz": "quiz",
            "The viva is on Friday": "viva",
            "The final exam": "exam",
            "Team meeting": "meeting",
            "Lecture on Monday": "class",
            "Class at 8 AM": "class",
            "Submit the project": "project",
            "Seminar on AI": "event",
            "College fest next week": "event",
            "Submit the lab record": None,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(classify_task_type(text), expected)

    def test_known_subjects_are_found_in_any_letter_case(self):
        self.assertEqual(extract_subject("operating systems quiz"), "Operating Systems")
        self.assertEqual(extract_subject("DBMS lab"), "DBMS")
        self.assertEqual(extract_subject("Discrete Mathematics quiz"), "Discrete Mathematics")

    def test_the_longest_known_subject_wins(self):
        self.assertEqual(extract_subject("Engineering Mathematics quiz"), "Engineering Mathematics")

    def test_unknown_subjects_are_found_from_capitalised_words(self):
        self.assertEqual(extract_subject("Submit Embedded Systems Assignment 2 by Friday"), "Embedded Systems")
        self.assertEqual(extract_subject("The Control Theory mid-sem exam is on 5 November"), "Control Theory")
        self.assertEqual(extract_subject("Please attend Theory of Automata lecture"), "Theory of Automata")

    def test_a_longer_capitalised_name_beats_a_shorter_known_name(self):
        self.assertEqual(extract_subject("Organic Chemistry Practical Viva on 9 November"), "Organic Chemistry")

    def test_instructions_and_event_names_are_not_mistaken_for_subjects(self):
        for text in (
            "Please attend the placement preparation workshop on 14 November",
            "Submit the internship report by Friday",
            "Kindly Submit Report by Friday",
            "Reminder: assignment due Friday",
            "The department seminar is on 13 November",
        ):
            with self.subTest(text=text):
                self.assertIsNone(extract_subject(text))

    def test_quiz_can_be_a_task_or_an_event(self):
        self.assertEqual(classify_message_category("Statistics quiz on Friday at 2 PM."), "event")
        self.assertEqual(classify_message_category("Please complete the Statistics quiz before 7 PM."), "task")

    def test_exam_is_an_event_unless_there_is_something_to_do(self):
        self.assertEqual(classify_message_category("The exam will be held on 10 November at 10 AM."), "event")
        self.assertEqual(classify_message_category("Study chapters 3 and 4 for the exam on 10 November."), "task")
        self.assertEqual(classify_message_category("The exam form must be submitted by 5 November."), "task")

    def test_registering_for_an_event_is_a_task(self):
        r = parse("Register for the college fest by 15th November.")
        self.assertEqual(classify_message_category("Register for the college fest by 15th November."), "task")
        self.assertEqual(r["due_date"], "2026-11-15")
        self.assertIsNone(r["event_datetime"])

    def test_classes_are_events(self):
        r = parse("Class tomorrow at 8 AM in room 204.")
        self.assertEqual(r["task_type"], "class")
        self.assertEqual(r["event_datetime"], "2026-10-13T08:00:00")
        self.assertTrue(is_event_message("Class tomorrow at 8 AM"))

    def test_deadline_messages_are_tasks(self):
        self.assertEqual(classify_message_category("The Data Mining assignment deadline is Monday."), "task")
        self.assertEqual(classify_message_category("Deadline for the lab report extended to 20th November."), "task")

    def test_general_notices(self):
        notices = [
            "Notice: the library will remain closed on 2 November 2026 for maintenance.",
            "The canteen will remain closed on 4 November for maintenance.",
            "The exam timetable has been published on the student portal.",
            "Quiz results have been declared.",
            "The exam schedule will be announced next week.",
            "College holiday on 2 November.",
            "All students are informed that semester registration opens tomorrow. Please check the portal.",
        ]
        for text in notices:
            with self.subTest(text=text):
                self.assertTrue(is_general_notice(text))
                self.assertEqual(classify_message_category(text), "general_notice")
                r = parse(text)
                self.assertIsNone(r["task_title"])
                self.assertIsNone(r["due_date"])  # a date in a notice must not leak out

    def test_a_message_that_asks_for_action_is_not_a_notice(self):
        self.assertFalse(is_general_notice("Registration opens tomorrow, register by 5 November."))
        self.assertFalse(is_general_notice("The library is closed; submit your books by Friday."))

    def test_chatter_is_not_a_task(self):
        r = parse("Hey, lunch at the canteen at 1 PM?")
        self.assertIsNone(r["task_title"])
        self.assertIsNone(r["due_time"])
        self.assertEqual(r["confidence"], 0.0)


# --------------------------------------------------
# STEP 19: missing fields
# --------------------------------------------------

class Step19MissingFieldTests(unittest.TestCase):
    def test_nothing_is_invented_for_a_bare_task(self):
        r = parse("Please submit your assignment.")
        self.assertEqual(r["task_title"], "Submit assignment")
        for field in ("due_date", "due_time", "event_datetime", "subject", "description", "date_time_expression"):
            self.assertIsNone(r[field], field)

    def test_a_deadline_that_is_unknown_stays_null(self):
        for text in (
            "Prepare and submit the Artificial Intelligence mini-project. The deadline has not been announced yet.",
            "Submit the report. The deadline is to be announced.",
            "Submit the report. The due date will be informed later, maybe 5 November.",
        ):
            with self.subTest(text=text):
                r = parse(text)
                self.assertIsNone(r["due_date"])
                self.assertIsNone(r["due_time"])

    def test_an_event_with_only_a_time_has_no_invented_date(self):
        r = parse("Please attend the project review meeting at 4 PM.")
        self.assertIsNone(r["event_datetime"])
        self.assertIsNone(r["due_time"])
        self.assertEqual(r["date_time_expression"], "4 PM")   # the words are kept

    def test_an_event_with_only_a_date_has_no_invented_time(self):
        r = parse("Seminar on Artificial Intelligence on 12 November.")
        self.assertIsNone(r["event_datetime"])
        self.assertIsNone(r["due_date"])
        self.assertEqual(r["date_time_expression"], "12 November")

    def test_events_use_event_datetime_and_tasks_use_due_fields(self):
        event = parse("DBMS quiz tomorrow at 10 am in room 204")
        self.assertEqual(event["event_datetime"], "2026-10-13T10:00:00")
        self.assertIsNone(event["due_date"])
        self.assertIsNone(event["due_time"])

        task = parse("Submit the DBMS lab record by 6 PM today.")
        self.assertEqual((task["due_date"], task["due_time"]), ("2026-10-12", "18:00"))
        self.assertIsNone(task["event_datetime"])

    def test_empty_and_odd_input_never_crashes(self):
        for value in ("", "   ", "\n\n", None, 12345, "!!!", "a" * 5000):
            with self.subTest(value=repr(value)[:30]):
                r = parse_message(value, "Manual input", REF)
                self.assertEqual(set(r), CONTRACT_KEYS)
                self.assertEqual(r["source"], "Manual input")
                self.assertEqual(r["change_information"], [])

    def test_empty_input_gives_empty_strings_not_none_for_raw_text(self):
        self.assertEqual(parse_message(None, "Manual input", REF)["raw_text"], "")

    def test_required_fields_are_present_even_when_null(self):
        r = parse("The exam timetable has been published on the student portal.", "LMS")
        self.assertEqual(r["source"], "LMS")
        self.assertEqual(r["raw_text"], "The exam timetable has been published on the student portal.")
        self.assertEqual(r["confidence"], 0.0)
        self.assertEqual(r["change_information"], [])

    def test_values_have_the_formats_of_the_contract(self):
        r = parse("The Operating Systems mid-semester exam will be held on 10 November 2026 at 10:30 AM.")
        self.assertRegex(r["event_datetime"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00$")
        r = parse("Submit the DBMS assignment by 5 November at 9 AM.")
        self.assertRegex(r["due_date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(r["due_time"], r"^\d{2}:\d{2}$")


# --------------------------------------------------
# STEP 20: confidence
# --------------------------------------------------

class Step20ConfidenceTests(unittest.TestCase):
    def test_score_is_a_quarter_for_each_core_fact(self):
        self.assertEqual(calculate_confidence(None, None, None, None), 0.0)
        self.assertEqual(calculate_confidence("t", None, None, None), 0.25)
        self.assertEqual(calculate_confidence("t", "exam", None, None), 0.5)
        self.assertEqual(calculate_confidence("t", "exam", "2026-11-05", None), 0.75)
        self.assertEqual(calculate_confidence("t", "exam", "2026-11-05", "10:00"), 1.0)

    def test_a_complete_task_scores_one(self):
        self.assertEqual(parse("Submit the DBMS assignment by 20th October at 5 PM.")["confidence"], 1.0)

    def test_a_complete_event_scores_one(self):
        # Before the fix an event could never score above 0.5.
        self.assertEqual(parse("DBMS quiz tomorrow at 10 am in room 204")["confidence"], 1.0)
        self.assertEqual(
            parse("The Physics practical viva is on 18 November 2026 at 1 PM.")["confidence"], 1.0)

    def test_missing_information_lowers_the_score(self):
        self.assertEqual(parse("Submit the DBMS assignment by 20th October.")["confidence"], 0.75)
        self.assertEqual(parse("Seminar on Artificial Intelligence on 12 November.")["confidence"], 0.75)
        self.assertEqual(parse("Please submit your assignment.")["confidence"], 0.5)

    def test_a_stated_unknown_deadline_does_not_count_as_found(self):
        r = parse("Prepare and submit the Artificial Intelligence mini-project. The deadline has not been announced yet.")
        self.assertEqual(r["confidence"], 0.5)

    def test_a_notice_scores_zero(self):
        self.assertEqual(parse("The exam timetable has been published on the student portal.")["confidence"], 0.0)

    def test_confidence_is_always_between_zero_and_one(self):
        messages = [
            "Submit the DBMS assignment by 20th October at 5 PM.",
            "Hey, lunch?", "", "Class tomorrow", "Quiz on Friday at 2 PM",
        ]
        for message in messages:
            with self.subTest(message=message):
                self.assertGreaterEqual(parse(message)["confidence"], 0.0)
                self.assertLessEqual(parse(message)["confidence"], 1.0)


# --------------------------------------------------
# STEP 21: representative messages
# --------------------------------------------------

class Step21DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = evaluate_step21.load_json(evaluate_step21.DEFAULT_DATASET)

    def test_dataset_has_25_unique_cases_with_all_expected_values(self):
        self.assertEqual(len(self.cases), 25)
        self.assertEqual(len({c["case_id"] for c in self.cases}), 25)
        for case in self.cases:
            self.assertEqual(set(case["expected"]), set(evaluate_step21.FIELDS), case["case_id"])
            self.assertIn(case["expected_category"], ("task", "event", "general_notice"))

    def test_every_case_matches_field_by_field(self):
        for case in self.cases:
            result = parse_message(case["raw_message"], case["source"], evaluate_step21.REFERENCE_DATE)
            for field in evaluate_step21.FIELDS:
                with self.subTest(case=case["case_id"], field=field):
                    self.assertEqual(result[field], case["expected"][field] or None)

    def test_every_case_has_the_expected_category(self):
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertEqual(
                    classify_message_category(case["raw_message"], evaluate_step21.REFERENCE_DATE),
                    case["expected_category"],
                )

    def test_scorer_reports_all_checks_passing(self):
        summary, failures = evaluate_step21.evaluate(self.cases)
        self.assertEqual(failures, [])
        self.assertEqual(summary["cases_fully_passing"], 25)
        self.assertEqual(summary["field_checks_passing"], 150)
        self.assertEqual(summary["field_checks"], 150)
        self.assertEqual(summary["category_checks_passing"], 25)

    def test_scorer_notices_a_wrong_expectation(self):
        wrong = [dict(self.cases[0], expected=dict(self.cases[0]["expected"], due_date="2030-01-01"))]
        summary, failures = evaluate_step21.evaluate(wrong)
        self.assertEqual(summary["cases_fully_passing"], 0)
        self.assertEqual([f[:2] for f in failures], [("NLP-01", "due_date")])


class HeldOutGeneralisationTests(unittest.TestCase):
    """Messages that are NOT in the dataset (reference date 2026-10-28).

    Each row: message, title, type, subject, due_date, due_time, event_datetime.
    """

    N = None
    CASES = [
        ("Kindly submit Data Mining Assignment 3 on Moodle by 9 November 2026 at 4:00 PM.",
         "Submit Data Mining Assignment 3", "assignment", "Data Mining", "2026-11-09", "16:00", N),
        ("Reminder: Physics assignment is due on 14 November.",
         "Submit Physics assignment", "assignment", "Physics", "2026-11-14", N, N),
        ("Submit your Statistics lab record by 8 PM today.",
         "Submit Statistics lab record", N, "Statistics", "2026-10-28", "20:00", N),
        ("The Data Structures mid-semester exam will be held on 12 November 2026 at 9:30 AM.",
         "Data Structures mid-semester exam", "exam", "Data Structures", N, N, "2026-11-12T09:30:00"),
        ("Machine Learning quiz on Thursday at 11 AM. Room details will follow.",
         "Machine Learning quiz", "quiz", "Machine Learning", N, N, "2026-10-29T11:00:00"),
        ("Our Operating Systems lecture starts tomorrow at 10:00 AM in Lab 2.",
         "Operating Systems lecture", "class", "Operating Systems", N, N, "2026-10-29T10:00:00"),
        ("Please finish the Discrete Mathematics assignment by tomorrow.",
         "Finish Discrete Mathematics assignment", "assignment", "Discrete Mathematics", "2026-10-29", N, N),
        ("The department workshop is scheduled for 20 November 2026 at 11:15 AM.",
         "Department workshop", "event", N, N, N, "2026-11-20T11:15:00"),
        ("The Web Technologies viva is on 19 November 2026 at 2 PM.",
         "Web Technologies viva", "viva", "Web Technologies", N, N, "2026-11-19T14:00:00"),
        ("Submit the lab report by 25 November 2026.",
         "Submit lab report", N, N, "2026-11-25", N, N),
        ("Please complete the Statistics quiz before 9 PM.",
         "Complete Statistics quiz", "quiz", "Statistics", N, "21:00", N),
        ("Notice: the canteen will remain closed on 4 November 2026 for maintenance.",
         N, N, N, N, N, N),
        ("Reminder: bring your admit card to campus tomorrow.",
         "Bring admit card to campus", N, N, "2026-10-29", N, N),
        ("The Computer Networks quiz is now rescheduled to 12 November 2026 at 3 PM.",
         "Computer Networks quiz rescheduled", "quiz", "Computer Networks", N, N, "2026-11-12T15:00:00"),
        # Subjects that are NOT in the SUBJECTS list:
        ("Please submit Embedded Systems Assignment 1 by 15 November 2026 at 5 PM.",
         "Submit Embedded Systems Assignment 1", "assignment", "Embedded Systems", "2026-11-15", "17:00", N),
        ("Reminder: Linear Algebra assignment is due on 16 November.",
         "Submit Linear Algebra assignment", "assignment", "Linear Algebra", "2026-11-16", N, N),
        ("The Organic Chemistry practical viva is on 21 November 2026 at 10 AM.",
         "Organic Chemistry practical viva", "viva", "Organic Chemistry", N, N, "2026-11-21T10:00:00"),
        # Other shapes of the same ideas:
        ("Operating Systems exam from 10 AM to 12 PM on 5th November.",
         "Operating Systems exam", "exam", "Operating Systems", N, N, "2026-11-05T10:00:00"),
        ("Submit the Physics assignment by 5th January at 5 PM.",
         "Submit Physics assignment", "assignment", "Physics", "2027-01-05", "17:00", N),
    ]

    def test_held_out_messages(self):
        reference = datetime(2026, 10, 28)
        names = ["task_title", "task_type", "subject", "due_date", "due_time", "event_datetime"]
        for message, *expected in self.CASES:
            result = parse_message(message, "Test", reference)
            for name, want in zip(names, expected):
                with self.subTest(message=message[:60], field=name):
                    self.assertEqual(result[name], want)


if __name__ == "__main__":
    unittest.main()
