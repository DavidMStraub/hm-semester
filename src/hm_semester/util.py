from datetime import date, timedelta
from dateutil.easter import easter


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
