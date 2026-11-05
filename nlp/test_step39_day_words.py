"""Tests for tomorrow / weekday / "next week" / "by Friday" wording, roadmap Step 39.

Run from the repository root:

    python -m unittest nlp.test_step39_day_words -v

Builds on Step 38 (see nlp/test_step38_relative_dates.py). The weekday tests
below compare the parser with a slow, independent calculation for every
reference day of one week.
"""

import unittest
from datetime import date, datetime, timedelta

from nlp.parser import extract_date, parse_message

WED = datetime(2026, 11, 4)  # Wednesday
NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse(text, ref=WED):
    return parse_message(text, "Chat", ref)


def upcoming(ref: date, weekday: int) -> date:
    """First day AFTER ref that is the given weekday (today does not count)."""
    day = ref + timedelta(days=1)
    while day.weekday() != weekday:
        day += timedelta(days=1)
    return day


def this_one(ref: date, weekday: int) -> date:
    """The given weekday, today included."""
    day = ref
    while day.weekday() != weekday:
        day += timedelta(days=1)
    return day


def next_week_one(ref: date, weekday: int) -> date:
    """The given weekday in the Monday-Sunday week AFTER ref's week."""
    day = ref
    while day.weekday() != 0:  # walk to Monday of this week
        day -= timedelta(days=1)
    day += timedelta(days=7)
    while day.weekday() != weekday:
        day += timedelta(days=1)
    return day


class EveryWeekdayEveryReferenceDay(unittest.TestCase):
    def test_plain_this_and_next(self):
        for offset in range(7):
            ref = datetime(2026, 11, 2) + timedelta(days=offset)  # Mon 2 Nov .. Sun 8 Nov
            for number, name in enumerate(NAMES):
                with self.subTest(today=ref.strftime("%A"), word=name):
                    self.assertEqual(
                        extract_date(f"Submit by {name}", ref),
                        upcoming(ref.date(), number).isoformat(),
                    )
                    self.assertEqual(
                        extract_date(f"Submit by this {name}", ref),
                        this_one(ref.date(), number).isoformat(),
                    )
                    self.assertEqual(
                        extract_date(f"Submit by next {name}", ref),
                        next_week_one(ref.date(), number).isoformat(),
                    )
                    self.assertEqual(
                        extract_date(f"Submit next week on {name}", ref),
                        next_week_one(ref.date(), number).isoformat(),
                    )

    def test_lower_and_upper_case(self):
        self.assertEqual(extract_date("submit by FRIDAY", WED), "2026-11-06")
        self.assertEqual(extract_date("submit by next friday", WED), "2026-11-13")


class TomorrowTests(unittest.TestCase):
    def test_tomorrow_spellings(self):
        for word in ("tomorrow", "Tomorrow", "tmrw", "tmr", "tomorow", "tommorow"):
            with self.subTest(word=word):
                self.assertEqual(extract_date(f"Submit the report {word}", WED), "2026-11-05")

    def test_day_after_tomorrow_spellings(self):
        self.assertEqual(extract_date("Submit the day after tmrw", WED), "2026-11-06")
        self.assertEqual(extract_date("Submit by the day after tomorrow", WED), "2026-11-06")

    def test_tomorrow_with_a_time_and_a_day_part(self):
        r = parse("Submit by tomorrow 5pm")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-05", "17:00"))
        r = parse("Submit tomorrow morning")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-05", None))
        self.assertEqual(r["date_time_expression"], "tomorrow morning")

    def test_today_and_this_evening(self):
        r = parse("Submit today evening")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-04", None))
        self.assertEqual(r["date_time_expression"], "today evening")
        r = parse("Submit this evening at 6 PM")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-04", "18:00"))
        self.assertEqual(extract_date("Submit this morning", WED), "2026-11-04")

    def test_tonight_is_unchanged(self):
        r = parse("Submit by tonight 11 PM")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-04", "23:00"))


class ShortWeekdayTests(unittest.TestCase):
    def test_short_names_after_by_on_before_till_due(self):
        self.assertEqual(extract_date("Submit the report by Fri", WED), "2026-11-06")
        self.assertEqual(extract_date("Submit on Mon", WED), "2026-11-09")
        self.assertEqual(extract_date("Submit before Thurs", WED), "2026-11-05")
        self.assertEqual(extract_date("Submit till Tues", WED), "2026-11-10")
        self.assertEqual(extract_date("Assignment due Sat", WED), "2026-11-07")
        self.assertEqual(extract_date("Submit by Thur.", WED), "2026-11-05")

    def test_this_and_next_with_short_names(self):
        self.assertEqual(extract_date("Submit by next Fri", WED), "2026-11-13")
        self.assertEqual(extract_date("Submit by this Fri", WED), "2026-11-06")
        self.assertEqual(extract_date("Submit next week on Fri", WED), "2026-11-13")

    def test_short_name_with_a_time_and_an_event(self):
        r = parse("Quiz on Wed at 10 AM")
        self.assertEqual(r["event_datetime"], "2026-11-11T10:00:00")
        self.assertEqual(r["date_time_expression"], "Wed at 10 AM")
        r = parse("Submit by Sat evening")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-07", None))

    def test_ordinary_words_are_not_days(self):
        for text in (
            "Submit the form, I sat there for an hour",
            "Submit the form while the sun is up",
            "Please submit the form, they wed in May",
            "Submit the form, the Wed of the page",   # no by/on/before/till/due before it
        ):
            with self.subTest(text=text):
                self.assertIsNone(extract_date(text, WED))


class ByFridayTests(unittest.TestCase):
    def test_by_before_till_on_or_before(self):
        for text in (
            "Submit by Friday",
            "Submit before Friday",
            "Submit till Friday",
            "Submit on or before Friday",
            "Submit it by this Friday",
        ):
            with self.subTest(text=text):
                self.assertEqual(extract_date(text, WED), "2026-11-06")

    def test_by_friday_with_time_and_day_part(self):
        r = parse("Submit on or before Friday 5pm")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-06", "17:00"))
        r = parse("Submit by Friday evening")
        self.assertEqual((r["due_date"], r["due_time"]), ("2026-11-06", None))
        self.assertEqual(r["date_time_expression"], "Friday evening")

    def test_an_explicit_date_beats_the_weekday_word(self):
        self.assertEqual(extract_date("Submit by Friday, 7 November 2026", WED), "2026-11-07")


class NextWeekTests(unittest.TestCase):
    def test_next_week_alone_is_still_no_date(self):
        for text in (
            "Submit the report next week",
            "Submit by the end of next week",
            "Submit by end of the week",
            "Submit this weekend",
        ):
            with self.subTest(text=text):
                self.assertIsNone(parse(text)["due_date"])

    def test_next_week_keeps_its_words_in_the_expression(self):
        self.assertEqual(parse("Submit the report next week")["date_time_expression"], "next week")

    def test_next_week_with_a_named_day_is_a_date(self):
        r = parse("Guest lecture on AI next week on Wednesday at 10 AM")
        self.assertEqual(r["event_datetime"], "2026-11-11T10:00:00")
        self.assertEqual(extract_date("Submit next week, Friday", WED), "2026-11-13")


class UnchangedBehaviourTests(unittest.TestCase):
    def test_a_change_message_still_gives_the_new_date(self):
        # Change detection itself is Steps 41-42 (nlp/test_step41_*, test_step42_*).
        r = parse("Project deadline moved from Friday to Monday for Smart Campus")
        self.assertEqual(r["due_date"], "2026-11-09")

    def test_the_output_keys_are_the_contract_keys(self):
        self.assertEqual(set(parse("Submit by Fri")), set(parse("hello")))

    def test_the_raw_text_is_kept(self):
        text = "Submit by Fri, 5 PM"
        self.assertEqual(parse(text)["raw_text"], text)


if __name__ == "__main__":
    unittest.main()
