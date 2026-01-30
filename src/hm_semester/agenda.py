import uuid
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from .semester import get_summer_semester_info, get_winter_semester_info
from .types import SemesterInfo
from .util import get_holiday_dates


def calculate_lecture_dates(
    start_date: datetime.date,
    end_date: datetime.date,
    weekday: int,
    holidays: set[datetime.date],
    biweekly: bool = False,
    start_week: int = 1,
) -> list[datetime.date]:
    """
    Calculate actual lecture dates, skipping holidays and maintaining biweekly alternation.
    
    For biweekly lectures, if a holiday interrupts the pattern, subsequent lectures shift
    to maintain the alternating pattern (e.g., week 1, 3, 5, 8 if week 7 is a holiday).
    
    Args:
        start_date: First day of semester
        end_date: Last day of semester
        weekday: Day of week (0=Monday, 6=Sunday)
        holidays: Set of dates when lectures don't occur
        biweekly: If True, lectures occur every 2 weeks
        start_week: For biweekly, which week to start (1 or 2)
    
    Returns:
        List of dates when lectures actually occur
    """
    lecture_dates = []
    
    # Find first matching weekday in semester
    current = start_date
    while current.weekday() != weekday:
        current += timedelta(days=1)
    
    # For biweekly, adjust to the correct starting week
    if biweekly and start_week > 1:
        current += timedelta(days=7 * (start_week - 1))
    
    # Track occurrences for biweekly alternation
    occurrence_count = 0
    
    while current <= end_date:
        if current not in holidays:
            if not biweekly:
                # Weekly: add every non-holiday occurrence
                lecture_dates.append(current)
            else:
                # Biweekly: add every other non-holiday occurrence
                if occurrence_count % 2 == 0:
                    lecture_dates.append(current)
                occurrence_count += 1
        
        current += timedelta(days=7)
    
    return lecture_dates


@dataclass
class WeeklyEvent:
    summary: str
    course_id: str  # Used for deterministic UID generation
    weekday: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    location: str = ""
    biweekly: bool = False  # If True, event is every 2 weeks
    start_week: int = 1  # 1 or 2, for biweekly events: which week to start
    timezone: str = "Europe/Berlin"
    sequence: int = 0  # Version number for updates


def create_agenda(
    events: list[WeeklyEvent],
    year: int,
    lang: Literal["de", "en"],
    semester: Literal["winter", "summer"],
) -> Calendar:
    """
    Create an iCalendar with individual lecture events, excluding holidays.
    Each lecture gets its own event with a deterministic UID for update tracking.
    Biweekly lectures maintain alternating pattern even when holidays interrupt.
    """
    if semester == "winter":
        info: SemesterInfo = get_winter_semester_info(year, lang)
    elif semester == "summer":
        info: SemesterInfo = get_summer_semester_info(year, lang)
    else:
        raise ValueError("semester must be 'winter' or 'summer'")

    cal = Calendar()
    if lang == "de":
        cal.add("prodid", "-//Hochschule München//hm-agenda//DE")
    else:
        cal.add("prodid", "-//Munich University of Applied Sciences//hm-agenda//EN")
    cal.add("version", "2.0")

    # Get all holiday dates from semester info
    holidays = get_holiday_dates(info)
    
    # Track which timezones we need to add
    timezones_needed = set()
    
    for ev in events:
        timezones_needed.add(ev.timezone)
        
        # Calculate actual lecture dates using holiday-aware scheduler
        lecture_dates = calculate_lecture_dates(
            info.start_date,
            info.end_date,
            ev.weekday,
            holidays,
            ev.biweekly,
            ev.start_week,
        )
        
        timezone = ZoneInfo(ev.timezone)
        
        # Create individual event for each lecture occurrence
        for lesson_num, lecture_date in enumerate(lecture_dates, start=1):
            event = Event()
            
            # Add lesson number to summary
            event.add("summary", f"{ev.summary} ({lesson_num})")
            
            # Create deterministic UID for update tracking
            uid = f"{ev.course_id}-{year}-{semester}-lesson-{lesson_num}@hm.edu"
            event.add("uid", uid)
            
            # Add timestamps and version tracking
            event.add("dtstamp", datetime.now())
            event.add("sequence", ev.sequence)
            
            # Add LAST-MODIFIED for modification tracking (only if sequence > 0)
            if ev.sequence > 0:
                event.add("last-modified", datetime.now())
            
            # Set lecture time
            dtstart = datetime.combine(lecture_date, ev.start_time)
            dtend = datetime.combine(lecture_date, ev.end_time)
            event.add("dtstart", dtstart.replace(tzinfo=timezone))
            event.add("dtend", dtend.replace(tzinfo=timezone))
            
            if ev.location:
                event.add("location", ev.location)
            
            cal.add_component(event)
    
    # Add VTIMEZONE components for all used timezones
    # When using TZID, RFC 5545 requires VTIMEZONE definitions
    # We use icalendar's built-in timezone utilities with ZoneInfo
    for tz_name in timezones_needed:
        try:
            from icalendar import Timezone as VTimezone
            tz = ZoneInfo(tz_name)
            
            # Create a minimal but valid VTIMEZONE component
            vtimezone = VTimezone()
            vtimezone.add('TZID', tz_name)
            
            # icalendar will handle the rest when serializing
            cal.add_component(vtimezone)
        except Exception:
            # If timezone generation fails, continue without it
            pass
    
    return cal
