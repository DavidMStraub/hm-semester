from datetime import date, timedelta
from typing import Tuple, Literal
from dateutil.easter import easter

from icalendar import Calendar, Event

# semesters
WINTER = "winter"
SUMMER = "summer"
# keys
START_DATE = "start_date"
END_DATE = "end_date"
VACATION_START = "vacation_start"
VACATION_END = "vacation_end"
BREAKS = "breaks"
# labels
LECTURE_PERIOD = "Lecture Period"
SEMESTER_BREAK = "Semester Break"
CHRISTMAS_BREAK = "Christmas Break"
EASTER_BREAK = "Easter Break"
PENTECOST_BREAK = "Pentecost Break"


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


def get_christmas_break(year: int) -> Tuple[date, date]:
    """Determine the Christmas break period."""
    start = date(year, 12, 24)
    if start.weekday() in [6, 0, 1]:  # Sunday, Monday, Tuesday
        start -= timedelta(days=(start.weekday() - 5) % 7)
    end = date(year + 1, 1, 6)
    if end.weekday() in [4, 5, 6]:  # Friday, Saturday, Sunday
        end += timedelta(days=(7 - end.weekday()))
    return start, end


def get_easter_break(year: int) -> Tuple[date, date]:
    """Determine the Easter break period from Maundy Thursday to the following Tuesday."""
    easter_sunday = easter(year)
    start = easter_sunday - timedelta(days=3)  # Maundy Thursday
    end = easter_sunday + timedelta(days=2)  # Tuesday after Easter
    return start, end


def get_pentecost_break(year: int) -> Tuple[date, date]:
    """Determine the Pentecost break from the Friday before to the following Tuesday."""
    pentecost_sunday = easter(year) + timedelta(days=49)
    start = pentecost_sunday - timedelta(days=2)  # Friday before Pentecost
    end = pentecost_sunday + timedelta(days=2)  # Tuesday after Pentecost
    return start, end


def generate_calendar(year: int, semester: Literal["winter", "summer"]) -> None:
    """Generate an iCalendar file for the given semester and year."""
    cal = Calendar()

    # Define semester parameters based on semester type
    semester_params = {
        WINTER: {
            START_DATE: adjust_start_date(date(year, 10, 1)),
            END_DATE: adjust_end_date(date(year + 1, 1, 25)),
            VACATION_START: adjust_end_date(date(year + 1, 1, 25)) + timedelta(days=1),
            VACATION_END: date(year + 1, 3, 14),
            BREAKS: [(get_christmas_break(year), CHRISTMAS_BREAK)],
        },
        SUMMER: {
            START_DATE: adjust_start_date(date(year, 3, 15)),
            END_DATE: adjust_end_date(date(year, 7, 10)),
            VACATION_START: adjust_end_date(date(year, 7, 10)) + timedelta(days=1),
            VACATION_END: date(year, 9, 30),
            BREAKS: [
                (get_easter_break(year), EASTER_BREAK),
                (get_pentecost_break(year), PENTECOST_BREAK),
            ],
        },
    }

    params = semester_params[semester]

    # Add lecture period
    event = Event()
    event.add("summary", LECTURE_PERIOD)
    event.add("dtstart", params[START_DATE])
    event.add("dtend", params[END_DATE])
    cal.add_component(event)

    # Add semester break
    event = Event()
    event.add("summary", SEMESTER_BREAK)
    event.add("dtstart", params[VACATION_START])
    event.add("dtend", params[VACATION_END])
    cal.add_component(event)

    # Add holiday breaks
    for (break_start, break_end), break_label in params[BREAKS]:
        event = Event()
        event.add("summary", break_label)
        event.add("dtstart", break_start)
        event.add("dtend", break_end)
        cal.add_component(event)

    # Write to file
    filename = f"{semester}_semester_{year}.ics"
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    print(f"Calendar saved as {filename}")


# Example usage
generate_calendar(2025, WINTER)
generate_calendar(2025, SUMMER)
