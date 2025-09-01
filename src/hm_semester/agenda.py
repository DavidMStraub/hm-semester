from datetime import datetime, time, timedelta
from typing import Literal, NamedTuple

from icalendar import Calendar, Event

from .semester import get_summer_semester_info, get_winter_semester_info
from .types import SemesterInfo


class WeeklyEvent(NamedTuple):
    summary: str
    weekday: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    location: str = ""


def create_agenda(
    events: list[WeeklyEvent],
    year: int,
    lang: Literal["de", "en"],
    semester: Literal["winter", "summer"],
) -> Calendar:
    """
    Create an iCalendar with weekly recurring events for the semester, excluding breaks.
    """
    if semester == "winter":
        info: SemesterInfo = get_winter_semester_info(year, lang)
    elif semester == "summer":
        info: SemesterInfo = get_summer_semester_info(year, lang)
    else:
        raise ValueError("semester must be 'winter' or 'summer'")

    cal = Calendar()
    cal.add("prodid", "-//Munich University of Applied Sciences//Agenda//EN")
    cal.add("version", "2.0")

    for ev in events:
        # Find the first date in the semester that matches the weekday
        d = info.start_date
        while d.weekday() != ev.weekday:
            d += timedelta(days=1)
        dtstart = datetime.combine(d, ev.start_time)
        dtend = datetime.combine(d, ev.end_time)
        event = Event()
        event.add("summary", ev.summary)
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
        if ev.location:
            event.add("location", ev.location)
        # RRULE: weekly until end of semester
        event.add(
            "rrule",
            {
                "freq": "weekly",
                "until": datetime.combine(info.end_date, ev.end_time),
            },
        )
        # EXDATE for all break days
        for break_start, break_end in info.breaks.values():
            exdate = break_start
            while exdate <= break_end:
                # Only exclude if it matches the weekday
                if exdate.weekday() == ev.weekday:
                    event.add("exdate", datetime.combine(exdate, ev.start_time))
                exdate += timedelta(days=1)
        cal.add_component(event)
    return cal
