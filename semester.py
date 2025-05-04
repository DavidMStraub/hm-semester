from datetime import date, datetime, timedelta
from typing import Literal
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
LABEL = "label"

# Define labels in both languages
LABELS = {
    "en": {
        "CHRISTMAS_BREAK": "Christmas Break",
        "EASTER_BREAK": "Easter Break",
        "PENTECOST_BREAK": "Pentecost Break",
        "START": "Start",
        "END": "End",
        "WINTER_SEMESTER": "Winter Semester",
        "SUMMER_SEMESTER": "Summer Semester",
    },
    "de": {
        "CHRISTMAS_BREAK": "Weihnachtsferien",
        "EASTER_BREAK": "Osterferien",
        "PENTECOST_BREAK": "Pfingstferien",
        "START": "Beginn",
        "END": "Ende",
        "WINTER_SEMESTER": "Wintersemester",
        "SUMMER_SEMESTER": "Sommersemester",
    },
}


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


def generate_calendar(
    year: int, semester: Literal["winter", "summer"], lang: Literal["de", "en"] = "en"
) -> None:
    """Generate an iCalendar file for the given semester and year in the specified language."""
    cal = Calendar()
    # Add required calendar properties for RFC 5545 compliance
    cal.add("prodid", "-//Munich University of Applied Sciences//Semester Calendar//EN")
    cal.add("version", "2.0")

    l = LABELS[lang]  # Get labels for the requested language

    # Define semester parameters based on semester type
    semester_params = {
        WINTER: {
            START_DATE: adjust_start_date(date(year, 10, 1)),
            END_DATE: adjust_end_date(date(year + 1, 1, 25)),
            VACATION_START: adjust_end_date(date(year + 1, 1, 25)) + timedelta(days=1),
            VACATION_END: date(year + 1, 3, 14),
            BREAKS: [(get_christmas_break(year), l["CHRISTMAS_BREAK"])],
            LABEL: l["WINTER_SEMESTER"],
        },
        SUMMER: {
            START_DATE: adjust_start_date(date(year, 3, 15)),
            END_DATE: adjust_end_date(date(year, 7, 10)),
            VACATION_START: adjust_end_date(date(year, 7, 10)) + timedelta(days=1),
            VACATION_END: date(year, 9, 30),
            BREAKS: [
                (get_easter_break(year), l["EASTER_BREAK"]),
                (get_pentecost_break(year), l["PENTECOST_BREAK"]),
            ],
            LABEL: l["SUMMER_SEMESTER"],
        },
    }

    params = semester_params[semester]

    # Add semester start (all-day event)
    event = Event()
    event.add("summary", f"{l['START']}: {params[LABEL]} (HM)")
    event.add("dtstart", params[START_DATE])
    event.add("dtend", params[START_DATE] + timedelta(days=1))  # End date is exclusive
    event.add("transp", "TRANSPARENT")  # Don't block time
    event["X-MICROSOFT-CDO-ALLDAYEVENT"] = "TRUE"  # Mark as all-day event
    # Add required event properties for RFC 5545 compliance
    event.add("dtstamp", datetime.now())
    event.add("uid", f"{semester}-start-{year}@hm-semester.example.com")
    cal.add_component(event)

    # Add semester end (all-day event)
    event = Event()
    event.add("summary", f"{l['END']}: {params[LABEL]} (HM)")
    event.add("dtstart", params[END_DATE])
    event.add("dtend", params[END_DATE] + timedelta(days=1))  # End date is exclusive
    event.add("transp", "TRANSPARENT")  # Don't block time
    event["X-MICROSOFT-CDO-ALLDAYEVENT"] = "TRUE"  # Mark as all-day event
    # Add required event properties for RFC 5545 compliance
    event.add("dtstamp", datetime.now())
    event.add("uid", f"{semester}-end-{year}@hm-semester.example.com")
    cal.add_component(event)

    # Add holiday breaks as multi-day events
    for i, ((break_start, break_end), break_label) in enumerate(params[BREAKS]):
        event = Event()
        event.add("summary", f"{break_label} (HM)")
        event.add("dtstart", break_start)
        event.add("dtend", break_end + timedelta(days=1))  # End date is exclusive
        # Add required event properties for RFC 5545 compliance
        event.add("dtstamp", datetime.now())
        event.add("uid", f"{semester}-break-{i}-{year}@hm-semester.example.com")
        cal.add_component(event)

    # Write to file
    filename = f"{semester}_semester_{year}_{lang}.ics"
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    print(f"Calendar saved as {filename}")


# Example usage
generate_calendar(2025, WINTER, "en")
generate_calendar(2025, SUMMER, "en")
generate_calendar(2025, WINTER, "de")
generate_calendar(2025, SUMMER, "de")
