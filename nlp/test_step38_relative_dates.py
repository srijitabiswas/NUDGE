"""Tests for relative date handling, roadmap Step 38.

Run from the repository root:

    python -m unittest nlp.test_step38_relative_dates -v

Decisions these tests record (approved by Prakriti):
  * "next Friday" is Friday of the FOLLOWING week (weeks run Monday-Sunday);
    "this Friday" is the upcoming Friday; plain "Friday" is the nearest
    upcoming Friday (a week away when today is Friday).
  * Slash dates are always DD/MM/YYYY and are never swapped.
  * "Sunday night" gives no time. "midnight" is 00:00 at the END of the named
    day, i.e. the next calendar day.
  * "next week" on its own still gives no date.
Weekdays of the reference dates used below are written next to them.
"""

import unittest
from datetime import datetime

from nlp.parser import extract_date, extract_time, parse_message

WED = datetime(2026, 11, 4)    # Wednesday
MON = datetime(2026, 11, 2)    # Monday
FRI = datetime(2026, 11, 6)    # Friday
SUN = datetime(2026, 11, 8)    # Sunday


def parse(text, ref=WED):
    return parse_message(text, "Chat", ref)


class InNDaysTests(unittest.TestCase):
    def test_in_days_with_a_time(self):
        r = parse("Submit the compiler lab writeup in 2 days at 5 PM.")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-06", "17:00"))
        self.assertEqual(r["date_time_expression"], "in 2 days at 5 PM")
        self.assertEqual(r["task_title"], "Submit compiler lab writeup")

    def test_in_weeks_and_number_words(self):
        self.assertEqual(extract_date("Submit in 3 weeks", WED), "2026-11-25")
        self.assertEqual(extract_date("Submit in two days", WED), "2026-11-06")
        self.assertEqual(extract_date("Submit in a week", WED), "2026-11-11")
        self.assertEqual(extract_date("Submit in 1 day", WED), "2026-11-05")

    def test_it_crosses_month_and_year_ends(self):
        self.assertEqual(extract_date("Submit in 2 days", datetime(2026, 12, 30)), "2027-01-01")
        self.assertEqual(extract_date("Submit in 3 days", datetime(2026, 10, 30)), "2026-11-02")

    def test_hours_and_within_are_not_read(self):
        self.assertIsNone(extract_date("Meeting in 2 hours", WED))
        self.assertIsNone(extract_date("Submit within 3 days", WED))  # not part of Step 38

    def test_a_word_containing_in_is_not_read(self):
        self.assertIsNone(extract_date("Login 2 days a week is needed", WED))


class DayAfterTomorrowTests(unittest.TestCase):
    def test_day_after_tomorrow_is_two_days_away(self):
        r = parse("Submit the form by the day after tomorrow.")
        self.assertEqual(r["due_date"], "2026-11-06")
        self.assertEqual(r["date_time_expression"], "the day after tomorrow")
        self.assertEqual(r["task_title"], "Submit form")

    def test_without_the(self):
        self.assertEqual(extract_date("Submit day after tomorrow", WED), "2026-11-06")

    def test_plain_tomorrow_is_unchanged(self):
        self.assertEqual(extract_date("Submit the report tomorrow", WED), "2026-11-05")

    def test_month_end(self):
        self.assertEqual(extract_date("Submit the day after tomorrow", datetime(2026, 10, 31)), "2026-11-02")


class WeekdayTests(unittest.TestCase):
    def test_plain_weekday_is_the_nearest_upcoming(self):
        self.assertEqual(extract_date("Submit by Friday", WED), "2026-11-06")
        self.assertEqual(extract_date("Submit by Tuesday", WED), "2026-11-10")
        self.assertEqual(extract_date("Submit by Friday", FRI), "2026-11-13")  # today is Friday

    def test_this_weekday_is_the_upcoming_one(self):
        self.assertEqual(extract_date("Submit by this Friday", WED), "2026-11-06")
        self.assertEqual(extract_date("Quiz this Monday", WED), "2026-11-09")
        self.assertEqual(extract_date("Submit by this Friday", FRI), "2026-11-06")  # today counts
        self.assertEqual(extract_date("Submit by coming Friday", WED), "2026-11-06")

    def test_next_weekday_is_in_the_following_week(self):
        self.assertEqual(extract_date("Submit by next Friday", WED), "2026-11-13")
        self.assertEqual(extract_date("Submit by next Friday", MON), "2026-11-13")
        self.assertEqual(extract_date("Submit by next Friday", FRI), "2026-11-13")
        self.assertEqual(extract_date("Submit by next Monday", WED), "2026-11-09")
        self.assertEqual(extract_date("Submit by next Monday", SUN), "2026-11-09")
        self.assertEqual(extract_date("Submit by next Monday", MON), "2026-11-09")
        self.assertEqual(extract_date("Submit by next Sunday", WED), "2026-11-15")

    def test_next_week_on_a_weekday_is_the_same_as_next_weekday(self):
        r = parse("Guest lecture on Artificial Intelligence next week on Wednesday at 10 AM.")
        self.assertEqual(r["event_datetime"], "2026-11-11T10:00:00")
        self.assertEqual(r["date_time_expression"], "next week on Wednesday at 10 AM")
        self.assertEqual(extract_date("Submit next week Friday", WED), "2026-11-13")

    def test_next_week_alone_is_still_no_date(self):
        self.assertIsNone(extract_date("Submit the report next week", WED))
        self.assertIsNone(parse("Submit the report next week")["due_date"])
        self.assertEqual(parse("Submit the report next week")["date_time_expression"], "next week")

    def test_next_week_with_a_far_weekday_is_not_joined(self):
        self.assertIsNone(extract_date("Submit next week. Friday is a holiday.", WED))

    def test_with_a_time(self):
        r = parse("Submit the assignment next Friday at 5 PM.")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-13", "17:00"))
        self.assertEqual(r["date_time_expression"], "next Friday at 5 PM")


class SlashDateTests(unittest.TestCase):
    def test_day_month_year(self):
        r = parse("Submit the assignment by 15/11/2026 at 18:00.")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-15", "18:00"))
        self.assertEqual(r["date_time_expression"], "15/11/2026 at 18:00")

    def test_the_order_is_never_swapped(self):
        self.assertEqual(extract_date("Submit by 05/06/2026", WED), "2026-06-05")
        self.assertEqual(extract_date("Submit by 1/2/2027", WED), "2027-02-01")

    def test_an_impossible_date_is_left_empty(self):
        self.assertIsNone(extract_date("Submit by 31/02/2026", WED))
        self.assertIsNone(extract_date("Submit by 12/25/2026", WED))  # month 25: not swapped
        self.assertIsNone(extract_date("Submit by 00/11/2026", WED))

    def test_other_slash_text_is_not_a_date(self):
        self.assertIsNone(extract_date("Marks are 3/4 of the total", WED))
        self.assertIsNone(extract_date("Version 15/11/20261 notes", WED))

    def test_an_explicit_date_beats_a_relative_word(self):
        self.assertEqual(extract_date("Submit tomorrow or by 20/11/2026", WED), "2026-11-20")


class MidnightTests(unittest.TestCase):
    def test_midnight_tonight_is_the_next_day_at_0000(self):
        r = parse("Please upload the project report by midnight tonight.")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-05", "00:00"))
        self.assertEqual(r["date_time_expression"], "midnight tonight")

    def test_midnight_on_a_weekday_is_the_day_after(self):
        r = parse("Submit by midnight on Sunday")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-09", "00:00"))
        self.assertEqual(r["date_time_expression"], "midnight on Sunday")

    def test_midnight_after_the_day_word(self):
        r = parse("Submit by tomorrow midnight")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-06", "00:00"))

    def test_midnight_alone_has_a_time_but_no_date(self):
        r = parse("Submit by midnight")
        self.assertIsNone(r["due_date"])
        self.assertEqual(r["due_time"], "00:00")

    def test_midnight_does_not_move_an_explicit_calendar_date(self):
        r = parse("Submit by midnight on 15 November 2026")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-15", "00:00"))

    def test_other_times_do_not_shift_the_date(self):
        r = parse("Submit by tonight 11 PM")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-04", "23:00"))

    def test_twelve_am_is_unchanged(self):
        self.assertEqual(extract_time("at 12 AM"), "00:00")


class PartOfDayTests(unittest.TestCase):
    def test_sunday_night_has_a_date_and_no_time(self):
        r = parse("Complete the assignment this weekend by Sunday night.")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-08", None))
        self.assertEqual(r["date_time_expression"], "Sunday night")

    def test_tomorrow_evening_keeps_the_words_and_no_time(self):
        r = parse("Submit the form tomorrow evening")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-05", None))
        self.assertEqual(r["date_time_expression"], "tomorrow evening")

    def test_a_stated_time_still_wins(self):
        r = parse("Submit by Sunday night 9 PM")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-08", "21:00"))


class UnchangedBehaviourTests(unittest.TestCase):
    def test_event_with_only_a_time_still_keeps_it_in_the_expression(self):
        r = parse_message("Seminar at 4 PM", "Chat", WED)
        self.assertIsNone(r["event_datetime"])
        self.assertIsNone(r["due_time"])
        self.assertEqual(r["date_time_expression"], "4 PM")

    def test_a_change_message_still_gives_the_new_date(self):
        # Change detection itself is Steps 41-42 (nlp/test_step41_*, test_step42_*).
        r = parse("Project deadline moved from 5 November to 8 November for Smart Campus")
        self.assertEqual(r["due_date"], "2026-11-08")

    def test_the_output_keys_are_the_contract_keys(self):
        self.assertEqual(set(parse("Submit in 2 days")), set(parse("hello")))

    def test_the_raw_text_is_kept(self):
        text = "Submit the form by the day after tomorrow."
        self.assertEqual(parse(text)["raw_text"], text)


if __name__ == "__main__":
    unittest.main()
