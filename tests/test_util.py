from datetime import date

from hm_semester.util import (
    adjust_end_date,
    adjust_start_date,
    get_christmas_break,
    get_easter_break,
    get_holiday_dates,
    get_pentecost_break,
    get_summer_semester_info,
    get_winter_semester_info,
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


# --- get_holiday_dates: Bavarian public holidays ---


def test_holiday_dates_summer_contains_ascension_day():
    # Christi Himmelfahrt 2026 = 14 May (Easter Apr 5 + 39 days)
    info = get_summer_semester_info(2026, "de")
    holidays = get_holiday_dates(info)
    assert date(2026, 5, 14) in holidays, "Christi Himmelfahrt should be a holiday"


def test_holiday_dates_summer_contains_corpus_christi():
    # Fronleichnam 2026 = 4 June (Easter Apr 5 + 60 days)
    info = get_summer_semester_info(2026, "de")
    holidays = get_holiday_dates(info)
    assert date(2026, 6, 4) in holidays, "Fronleichnam should be a holiday"


def test_holiday_dates_summer_contains_labour_day():
    # Tag der Arbeit = 1 May, always within summer semester
    info = get_summer_semester_info(2026, "de")
    holidays = get_holiday_dates(info)
    assert date(2026, 5, 1) in holidays, "1. Mai (Tag der Arbeit) should be a holiday"


def test_holiday_dates_summer_contains_pentecost_monday():
    # Pfingstmontag 2026 = 25 May; falls within summer semester
    info = get_summer_semester_info(2026, "de")
    holidays = get_holiday_dates(info)
    assert date(2026, 5, 25) in holidays, "Pfingstmontag should be a holiday"


def test_holiday_dates_summer_contains_easter_break_days():
    # Easter break should still be included (from semester breaks)
    info = get_summer_semester_info(2026, "de")
    holidays = get_holiday_dates(info)
    # Good Friday 2026 = 3 April, Easter Monday = 6 April
    assert date(2026, 4, 3) in holidays, "Karfreitag should be in holidays"
    assert date(2026, 4, 6) in holidays, "Ostermontag should be in holidays"


def test_holiday_dates_winter_contains_tag_der_deutschen_einheit():
    # Tag der Deutschen Einheit = 3 October, always within winter semester
    info = get_winter_semester_info(2025, "de")
    holidays = get_holiday_dates(info)
    assert date(2025, 10, 3) in holidays, "Tag der Deutschen Einheit should be a holiday"


def test_holiday_dates_winter_contains_allerheiligen():
    # Allerheiligen = 1 November, Bavarian-specific holiday
    info = get_winter_semester_info(2025, "de")
    holidays = get_holiday_dates(info)
    assert date(2025, 11, 1) in holidays, "Allerheiligen should be a holiday"


def test_holiday_dates_winter_contains_christmas_break():
    # Christmas break days should be included
    info = get_winter_semester_info(2025, "de")
    holidays = get_holiday_dates(info)
    assert date(2025, 12, 24) in holidays, "Christmas Eve should be in holidays"
    assert date(2026, 1, 1) in holidays, "New Year's Day should be in holidays"


def test_holiday_dates_outside_semester_not_included():
    # Fronleichnam 2026 = 4 June is well outside winter semester
    info = get_winter_semester_info(2025, "de")
    holidays = get_holiday_dates(info)
    assert date(2026, 6, 4) not in holidays, "Summer holiday should not appear in winter semester"
