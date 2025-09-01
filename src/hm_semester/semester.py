from datetime import datetime, timedelta
from typing import Literal

from icalendar import Calendar, Event

from .const import LABELS, SUMMER, WINTER
from .util import get_summer_semester_info, get_winter_semester_info


def generate_calendar(
    year: int, semester: Literal["winter", "summer"], lang: Literal["de", "en"] = "en"
) -> Calendar:
    """Generate an iCalendar file for the given semester and year in the specified language."""
    cal = Calendar()
    # Add required calendar properties for RFC 5545 compliance
    cal.add("prodid", "-//Munich University of Applied Sciences//Semester Calendar//EN")
    cal.add("version", "2.0")

    l = LABELS[lang]  # Get labels for the requested language

    if semester == WINTER:
        params = get_winter_semester_info(year, lang)
    elif semester == SUMMER:
        params = get_summer_semester_info(year, lang)
    else:
        raise ValueError(f"Unknown semester: {semester}")


    # Add semester start (all-day event)
    event = Event()
    event.add("summary", f"{l['START']}: {params.label} (HM)")
    event.add("dtstart", params.start_date)
    event.add("dtend", params.start_date + timedelta(days=1))  # End date is exclusive
    event.add("transp", "TRANSPARENT")  # Don't block time
    event["X-MICROSOFT-CDO-ALLDAYEVENT"] = "TRUE"  # Mark as all-day event
    # Add required event properties for RFC 5545 compliance
    event.add("dtstamp", datetime.now())
    event.add("uid", f"{semester}-start-{year}@hm-semester.example.com")
    cal.add_component(event)

    # Add semester end (all-day event)
    event = Event()
    event.add("summary", f"{l['END']}: {params.label} (HM)")
    event.add("dtstart", params.end_date)
    event.add("dtend", params.end_date + timedelta(days=1))  # End date is exclusive
    event.add("transp", "TRANSPARENT")  # Don't block time
    event["X-MICROSOFT-CDO-ALLDAYEVENT"] = "TRUE"  # Mark as all-day event
    # Add required event properties for RFC 5545 compliance
    event.add("dtstamp", datetime.now())
    event.add("uid", f"{semester}-end-{year}@hm-semester.example.com")
    cal.add_component(event)

    # Add holiday breaks as multi-day events
    for i, (break_label, (break_start, break_end)) in enumerate(params.breaks.items()):
        event = Event()
        event.add("summary", f"{break_label} (HM)")
        event.add("dtstart", break_start)
        event.add("dtend", break_end + timedelta(days=1))  # End date is exclusive
        # Add required event properties for RFC 5545 compliance
        event.add("dtstamp", datetime.now())
        event.add("uid", f"{semester}-break-{i}-{year}@hm-semester.example.com")
        cal.add_component(event)

    return cal
