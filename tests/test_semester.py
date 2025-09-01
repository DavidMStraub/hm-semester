from datetime import date
from hm_semester.util import (
    adjust_start_date,
    adjust_end_date,
    get_christmas_break,
    get_easter_break,
    get_pentecost_break,
)


def test_adjust_start_date_monday():
    assert adjust_start_date(date(2025, 3, 17)) == date(2025, 3, 17)


def test_adjust_start_date_friday():
    assert adjust_start_date(date(2025, 3, 14)) == date(2025, 3, 17)


def test_adjust_start_date_sunday():

    assert adjust_start_date(date(2025, 3, 16)) == date(2025, 3, 17)


def test_adjust_end_date_friday():
    assert adjust_end_date(date(2025, 3, 14)) == date(2025, 3, 14)


def test_adjust_end_date_sunday():
    assert adjust_end_date(date(2025, 3, 16)) == date(2025, 3, 14)


def test_get_christmas_break():
    start, end = get_christmas_break(2025)
    assert start.month == 12 and start.day == 24
    assert end.month == 1 and end.day == 6


def test_get_easter_break():
    start, end = get_easter_break(2025)
    # Easter 2025 is April 20, so break should start April 17
    assert start == date(2025, 4, 17)
    assert end == date(2025, 4, 22)


def test_get_pentecost_break():
    start, end = get_pentecost_break(2025)
    # Pentecost 2025 is June 8, so break should start June 6
    assert start == date(2025, 6, 6)
    assert end == date(2025, 6, 10)
