from datetime import date, timedelta

from dateutil.easter import easter

from .const import LABELS
from .types import SemesterInfo


def adjust_start_date(start_date: date) -> date:
    """Adjust start date to the next Monday if it falls on a Friday, Saturday, or Sunday."""
    if start_date.weekday() in [4, 5, 6]:
        return start_date + timedelta(days=(7 - start_date.weekday()))
    return start_date


def adjust_end_date(end_date: date) -> date:
    """Adjust end date to the previous Friday if it falls on a Saturday, Sunday, or Monday."""
    if end_date.weekday() in [5, 6, 0]:
        return end_date - timedelta(days=(end_date.weekday() - 4) % 7)
    return end_date


def get_christmas_break(year: int) -> tuple[date, date]:
    """Determine the Christmas break period."""
    start = date(year, 12, 24)
    if start.weekday() in [6, 0, 1]:  # Sunday, Monday, Tuesday
        start -= timedelta(days=(start.weekday() - 5) % 7)
    end = date(year + 1, 1, 6)
    if end.weekday() in [4, 5, 6]:  # Friday, Saturday, Sunday
        end += timedelta(days=(7 - end.weekday()))
    return start, end


def get_easter_break(year: int) -> tuple[date, date]:
    """Determine the Easter break period from Maundy Thursday to the following Tuesday."""
    easter_sunday = easter(year)
    start = easter_sunday - timedelta(days=3)  # Maundy Thursday
    end = easter_sunday + timedelta(days=2)  # Tuesday after Easter
    return start, end


def get_pentecost_break(year: int) -> tuple[date, date]:
    """Determine the Pentecost break from the Friday before to the following Tuesday."""
    pentecost_sunday = easter(year) + timedelta(days=49)
    start = pentecost_sunday - timedelta(days=2)  # Friday before Pentecost
    end = pentecost_sunday + timedelta(days=2)  # Tuesday after Pentecost
    return start, end


def get_holiday_dates(semester_info: SemesterInfo) -> set[date]:
    """
    Return a set of all dates when lectures do not take place.
    This includes all days within semester breaks.
    
    Args:
        semester_info: The semester information containing break periods
        
    Returns:
        Set of dates when lectures do not occur
    """
    holidays = set()
    for break_start, break_end in semester_info.breaks.values():
        current = break_start
        while current <= break_end:
            holidays.add(current)
            current += timedelta(days=1)
    return holidays


def get_winter_semester_info(year: int, lang: str) -> SemesterInfo:
    l = LABELS[lang]
    start_date = adjust_start_date(date(year, 10, 1))
    end_date = adjust_end_date(date(year + 1, 1, 25))
    vacation_start = end_date + timedelta(days=1)
    vacation_end = date(year + 1, 3, 14)
    breaks: dict[str, tuple[date, date]] = {
        l["CHRISTMAS_BREAK"]: get_christmas_break(year)
    }
    label = l["WINTER_SEMESTER"]
    return SemesterInfo(
        start_date=start_date,
        end_date=end_date,
        vacation_start=vacation_start,
        vacation_end=vacation_end,
        breaks=breaks,
        label=label,
    )


def get_summer_semester_info(year: int, lang: str) -> SemesterInfo:
    l = LABELS[lang]
    start_date = adjust_start_date(date(year, 3, 15))
    end_date = adjust_end_date(date(year, 7, 10))
    vacation_start = end_date + timedelta(days=1)
    vacation_end = date(year, 9, 30)
    breaks: dict[str, tuple[date, date]] = {
        l["EASTER_BREAK"]: get_easter_break(year),
        l["PENTECOST_BREAK"]: get_pentecost_break(year),
    }
    label = l["SUMMER_SEMESTER"]
    return SemesterInfo(
        start_date=start_date,
        end_date=end_date,
        vacation_start=vacation_start,
        vacation_end=vacation_end,
        breaks=breaks,
        label=label,
    )
