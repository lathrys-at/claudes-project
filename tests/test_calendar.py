"""Tests for the calendar/date library example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
import io
import sys
import datetime
import calendar


@pytest.fixture(scope="module")
def calendar_env_and_output():
    """Load the calendar.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "calendar.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


def eval_in_env(source, env):
    """Helper to evaluate Pebble source and return the result."""
    return eval_source(source, env)


class TestCalendar:
    """Tests for the calendar/date library."""

    def test_example_output(self, calendar_env_and_output):
        """Test that the example file produces demo output without errors."""
        env, demo_output = calendar_env_and_output
        # Check that output is non-empty and contains expected dates
        assert "2026-06-03" in demo_output
        assert "Wednesday" in demo_output

    def test_leap_year_basic(self, calendar_env_and_output):
        """Test leap-year? for basic cases."""
        env, _ = calendar_env_and_output

        # 2024 is leap (divisible by 4, not a century)
        assert eval_in_env("(leap-year? 2024)", env) is True

        # 2025 is not leap
        assert eval_in_env("(leap-year? 2025)", env) is False

        # 2000 is leap (divisible by 400)
        assert eval_in_env("(leap-year? 2000)", env) is True

        # 1900 is not leap (century not divisible by 400)
        assert eval_in_env("(leap-year? 1900)", env) is False

    def test_leap_year_comprehensive(self, calendar_env_and_output):
        """Test leap-year? against Python's calendar.isleap for many years."""
        env, _ = calendar_env_and_output

        # Test all years from 1 to 2400 (representative range)
        # Sample every 4th year to keep test fast but still comprehensive
        test_years = list(range(1, 2401, 4))
        # Also add all century years for extra coverage
        test_years.extend([1700, 1800, 1900, 1901, 2000, 2001, 2100, 2400])
        test_years = sorted(set(test_years))

        for year in test_years:
            pebble_result = eval_in_env(f"(leap-year? {year})", env)
            python_result = calendar.isleap(year)
            assert pebble_result == python_result, (
                f"leap-year? mismatch for {year}: Pebble={pebble_result}, Python={python_result}"
            )

    def test_days_in_month_february(self, calendar_env_and_output):
        """Test days-in-month for February in leap and common years."""
        env, _ = calendar_env_and_output

        # February 2024 (leap year)
        assert eval_in_env("(days-in-month 2024 2)", env) == 29

        # February 2025 (common year)
        assert eval_in_env("(days-in-month 2025 2)", env) == 28

        # February 2000 (leap year, divisible by 400)
        assert eval_in_env("(days-in-month 2000 2)", env) == 29

        # February 1900 (common year, divisible by 100 but not 400)
        assert eval_in_env("(days-in-month 1900 2)", env) == 28

    def test_days_in_month_all_months(self, calendar_env_and_output):
        """Test days-in-month for all months in a sample year."""
        env, _ = calendar_env_and_output

        expected = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }

        for month, days in expected.items():
            result = eval_in_env(f"(days-in-month 2025 {month})", env)
            assert result == days, f"Month {month} should have {days} days, got {result}"

    def test_days_in_month_oracle(self, calendar_env_and_output):
        """Test days-in-month against Python's calendar.monthrange for many (year, month) pairs."""
        env, _ = calendar_env_and_output

        # Test a representative sample of years and all months
        test_years = [1900, 1901, 2000, 2001, 2024, 2025, 2026, 2099, 2100, 2101]
        for year in test_years:
            for month in range(1, 13):
                pebble_result = eval_in_env(f"(days-in-month {year} {month})", env)
                python_result = calendar.monthrange(year, month)[1]
                assert pebble_result == python_result, (
                    f"days-in-month mismatch for {year}-{month:02d}: "
                    f"Pebble={pebble_result}, Python={python_result}"
                )

    def test_valid_date_true(self, calendar_env_and_output):
        """Test valid-date? returns true for real dates."""
        env, _ = calendar_env_and_output

        # Valid dates
        assert eval_in_env("(valid-date? 2026 6 3)", env) is True
        assert eval_in_env("(valid-date? 2024 2 29)", env) is True  # Leap year
        assert eval_in_env("(valid-date? 2026 12 31)", env) is True
        assert eval_in_env("(valid-date? 1 1 1)", env) is True

    def test_valid_date_false(self, calendar_env_and_output):
        """Test valid-date? returns false for invalid dates."""
        env, _ = calendar_env_and_output

        # Invalid dates
        assert eval_in_env("(valid-date? 2025 2 29)", env) is False  # Not a leap year
        assert eval_in_env("(valid-date? 2026 13 1)", env) is False  # Month > 12
        assert eval_in_env("(valid-date? 2026 0 1)", env) is False   # Month < 1
        assert eval_in_env("(valid-date? 2026 4 31)", env) is False  # April has 30 days
        assert eval_in_env("(valid-date? 2026 1 0)", env) is False   # Day < 1
        assert eval_in_env("(valid-date? 0 1 1)", env) is False      # Year < 1

    def test_day_of_year_basic(self, calendar_env_and_output):
        """Test day-of-year for basic dates."""
        env, _ = calendar_env_and_output

        # January 1 should be day 1
        assert eval_in_env("(day-of-year 2026 1 1)", env) == 1

        # January 2 should be day 2
        assert eval_in_env("(day-of-year 2026 1 2)", env) == 2

        # December 31 in common year (2025) should be day 365
        assert eval_in_env("(day-of-year 2025 12 31)", env) == 365

        # December 31 in leap year (2024) should be day 366
        assert eval_in_env("(day-of-year 2024 12 31)", env) == 366

        # February 29 in leap year (2024) should be day 60
        assert eval_in_env("(day-of-year 2024 2 29)", env) == 60

    def test_day_of_year_oracle(self, calendar_env_and_output):
        """Test day-of-year against Python's datetime for a sampling of dates."""
        env, _ = calendar_env_and_output

        # Test various dates across multiple years
        test_dates = [
            (2024, 1, 1), (2024, 2, 29), (2024, 12, 31),
            (2025, 1, 1), (2025, 12, 31),
            (2000, 1, 1), (2000, 2, 29), (2000, 12, 31),
            (1900, 1, 1), (1900, 12, 31),
            (2026, 6, 3),  # Today
        ]

        for year, month, day in test_dates:
            pebble_result = eval_in_env(f"(day-of-year {year} {month} {day})", env)
            python_result = datetime.date(year, month, day).timetuple().tm_yday
            assert pebble_result == python_result, (
                f"day-of-year mismatch for {year}-{month:02d}-{day:02d}: "
                f"Pebble={pebble_result}, Python={python_result}"
            )

    def test_day_of_week_basic(self, calendar_env_and_output):
        """Test day-of-week returns valid weekday names."""
        env, _ = calendar_env_and_output

        result = eval_in_env("(day-of-week 2026 6 3)", env)
        assert result == "Wednesday"

        # Check that we get one of the valid weekday names
        valid_names = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
        assert result in valid_names

    def test_day_of_week_known_dates(self, calendar_env_and_output):
        """Test day-of-week for dates with known weekdays."""
        env, _ = calendar_env_and_output

        # These are real dates with known weekdays (verify via Python's datetime)
        test_cases = [
            (2024, 1, 1, "Monday"),
            (2024, 2, 14, "Wednesday"),
            (2024, 12, 25, "Wednesday"),
            (2025, 1, 1, "Wednesday"),
            (2000, 1, 1, "Saturday"),
            (2000, 12, 31, "Sunday"),
            (1900, 1, 1, "Monday"),
        ]

        for year, month, day, expected_day in test_cases:
            result = eval_in_env(f"(day-of-week {year} {month} {day})", env)
            assert result == expected_day, (
                f"day-of-week mismatch for {year}-{month:02d}-{day:02d}: "
                f"expected {expected_day}, got {result}"
            )

    def test_day_of_week_oracle(self, calendar_env_and_output):
        """Test day-of-week against Python's datetime for hundreds of dates."""
        env, _ = calendar_env_and_output

        # Map Python's weekday() (0=Monday..6=Sunday) to English names
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Test the first day of every month from 1900 to 2100 (inclusive)
        # This covers 201 years * 12 months = 2412 dates
        for year in range(1900, 2101):
            for month in range(1, 13):
                day = 1
                pebble_result = eval_in_env(f"(day-of-week {year} {month} {day})", env)
                python_date = datetime.date(year, month, day)
                python_result = weekday_names[python_date.weekday()]
                assert pebble_result == python_result, (
                    f"day-of-week mismatch for {year}-{month:02d}-{day:02d}: "
                    f"Pebble={pebble_result}, Python={python_result}"
                )

    def test_date_to_string_basic(self, calendar_env_and_output):
        """Test date->string for basic dates."""
        env, _ = calendar_env_and_output

        assert eval_in_env("(date->string 2026 6 3)", env) == "2026-06-03"
        assert eval_in_env("(date->string 2026 1 1)", env) == "2026-01-01"
        assert eval_in_env("(date->string 2026 12 31)", env) == "2026-12-31"

    def test_date_to_string_padding(self, calendar_env_and_output):
        """Test date->string zero-padding for single-digit month and day."""
        env, _ = calendar_env_and_output

        # Single-digit month and day
        assert eval_in_env("(date->string 2026 1 5)", env) == "2026-01-05"
        assert eval_in_env("(date->string 2026 7 9)", env) == "2026-07-09"

        # Double-digit but with leading zero
        assert eval_in_env("(date->string 2026 10 9)", env) == "2026-10-09"

    def test_days_between_basic(self, calendar_env_and_output):
        """Test days-between for basic date pairs."""
        env, _ = calendar_env_and_output

        # Same date should be 0 days apart
        assert eval_in_env("(days-between 2026 6 3 2026 6 3)", env) == 0

        # One day later
        assert eval_in_env("(days-between 2026 6 3 2026 6 4)", env) == 1

        # One day earlier (negative)
        assert eval_in_env("(days-between 2026 6 4 2026 6 3)", env) == -1

    def test_days_between_across_months(self, calendar_env_and_output):
        """Test days-between across month boundaries."""
        env, _ = calendar_env_and_output

        # From end of May to start of June (31 days in May)
        result = eval_in_env("(days-between 2026 5 31 2026 6 1)", env)
        assert result == 1

        # From end of June to start of July (30 days in June)
        result = eval_in_env("(days-between 2026 6 30 2026 7 1)", env)
        assert result == 1

    def test_days_between_across_years(self, calendar_env_and_output):
        """Test days-between across year boundaries."""
        env, _ = calendar_env_and_output

        # From Dec 31 to Jan 1 of next year (1 day)
        result = eval_in_env("(days-between 2025 12 31 2026 1 1)", env)
        assert result == 1

        # Reversed
        result = eval_in_env("(days-between 2026 1 1 2025 12 31)", env)
        assert result == -1

    def test_days_between_leap_day(self, calendar_env_and_output):
        """Test days-between across leap day."""
        env, _ = calendar_env_and_output

        # From Feb 28 to Feb 29 in leap year (1 day)
        result = eval_in_env("(days-between 2024 2 28 2024 2 29)", env)
        assert result == 1

        # From Feb 29 to Mar 1 in leap year (1 day)
        result = eval_in_env("(days-between 2024 2 29 2024 3 1)", env)
        assert result == 1

    def test_days_between_oracle(self, calendar_env_and_output):
        """Test days-between against Python's datetime for various date pairs."""
        env, _ = calendar_env_and_output

        test_pairs = [
            ((2024, 1, 1), (2024, 1, 2)),
            ((2024, 1, 1), (2024, 2, 1)),
            ((2024, 1, 1), (2025, 1, 1)),
            ((2024, 2, 28), (2024, 2, 29)),
            ((2024, 2, 29), (2024, 3, 1)),
            ((2025, 2, 28), (2025, 3, 1)),
            ((2000, 1, 1), (2000, 12, 31)),
            ((1900, 1, 1), (2000, 1, 1)),
            ((2026, 6, 3), (2026, 1, 1)),
        ]

        for (y1, m1, d1), (y2, m2, d2) in test_pairs:
            pebble_result = eval_in_env(f"(days-between {y1} {m1} {d1} {y2} {m2} {d2})", env)
            python_result = (datetime.date(y2, m2, d2) - datetime.date(y1, m1, d1)).days
            assert pebble_result == python_result, (
                f"days-between mismatch for {y1}-{m1:02d}-{d1:02d} to {y2}-{m2:02d}-{d2:02d}: "
                f"Pebble={pebble_result}, Python={python_result}"
            )

            # Also test that reversed pair gives negation
            pebble_reversed = eval_in_env(f"(days-between {y2} {m2} {d2} {y1} {m1} {d1})", env)
            assert pebble_reversed == -pebble_result, (
                f"days-between reversed mismatch for {y2}-{m2:02d}-{d2:02d} to {y1}-{m1:02d}-{d1:02d}: "
                f"expected {-pebble_result}, got {pebble_reversed}"
            )
