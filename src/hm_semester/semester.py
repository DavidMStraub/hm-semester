from datetime import date, datetime, timedelta
from typing import Literal

from icalendar import Calendar, Event

from .const import (
    BREAKS,
    END_DATE,
    LABEL,
    LABELS,
    START_DATE,
    SUMMER,
    VACATION_END,
    VACATION_START,
    WINTER,
)
from .util import (
    adjust_end_date,
    adjust_start_date,
    get_christmas_break,
    get_easter_break,
    get_pentecost_break,
)


def generate_calendar(
    year: int, semester: Literal["winter", "summer"], lang: Literal["de", "en"] = "en"
) -> Calendar:
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

    return cal
