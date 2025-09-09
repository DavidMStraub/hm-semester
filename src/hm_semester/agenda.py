import uuid
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from .semester import get_summer_semester_info, get_winter_semester_info
from .types import SemesterInfo


@dataclass
class WeeklyEvent:
    summary: str
    weekday: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    location: str = ""
    biweekly: bool = False  # If True, event is every 2 weeks
    start_week: int = 1  # 1 or 2, for biweekly events: which week to start
    timezone: str = "Europe/Berlin"


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
        if ev.biweekly:
            # Week 1: start on first matching weekday
            # Week 2: start on first matching weekday + 7 days
            if ev.start_week == 2:
                d += timedelta(days=7)
        dtstart = datetime.combine(d, ev.start_time)
        dtend = datetime.combine(d, ev.end_time)
        event = Event()
        event.add("summary", ev.summary)
        timezone = ZoneInfo(ev.timezone)
        event.add("dtstart", dtstart.replace(tzinfo=timezone))
        event.add("dtend", dtend.replace(tzinfo=timezone))
        event.add("uid", str(uuid.uuid4()))
        if ev.location:
            event.add("location", ev.location)
        rrule = {
            "freq": "weekly",
            "until": datetime.combine(info.end_date, ev.end_time).replace(
                tzinfo=timezone
            ),
        }
        if ev.biweekly:
            rrule["interval"] = 2
        event.add("rrule", rrule)
        for break_start, break_end in info.breaks.values():
            exdate = break_start
            while exdate <= break_end:
                if exdate.weekday() == ev.weekday:
                    event.add(
                        "exdate",
                        datetime.combine(exdate, ev.start_time).replace(
                            tzinfo=timezone
                        ),
                    )
                exdate += timedelta(days=1)
        cal.add_component(event)
    return cal
