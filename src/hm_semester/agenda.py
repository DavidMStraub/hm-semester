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
        start_week: Which week to start (1, 2, 3, 4, etc.) - first lecture occurs in this week
    
    Returns:
        List of dates when lectures actually occur
    """
    lecture_dates = []
    
    # Find first matching weekday in semester
    current = start_date
    while current.weekday() != weekday:
        current += timedelta(days=1)
    
    # For biweekly, we need to track week numbers from semester start
    # and include only weeks matching the pattern based on start_week
    week_number = 1
    
    # Default start_week to 1 if not specified
    if start_week is None:
        start_week = 1
    
    # Skip to the starting week
    if start_week > 1:
        weeks_to_skip = start_week - 1
        current += timedelta(days=7 * weeks_to_skip)
        week_number = start_week
    
    while current <= end_date:
        if current not in holidays:
            if not biweekly:
                # Weekly: add every non-holiday occurrence
                lecture_dates.append(current)
            else:
                # Biweekly: add only if week matches the pattern
                # Pattern is determined by start_week parity
                if (week_number - start_week) % 2 == 0:
                    lecture_dates.append(current)
        
        current += timedelta(days=7)
        week_number += 1
    
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
    start_week: int = 1  # Which semester week to start (1, 2, 3, 4, etc.)
    max_reps: int | None = None  # Maximum number of occurrences (None = unlimited)
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
        
        # Limit to max_reps if specified
        if ev.max_reps is not None:
            lecture_dates = lecture_dates[:ev.max_reps]
        
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
            
            # Set lecture time in local timezone, then convert to UTC
            # This properly handles daylight saving time transitions
            dtstart = datetime.combine(lecture_date, ev.start_time, tzinfo=timezone)
            dtend = datetime.combine(lecture_date, ev.end_time, tzinfo=timezone)
            event.add("dtstart", dtstart.astimezone(ZoneInfo('UTC')))
            event.add("dtend", dtend.astimezone(ZoneInfo('UTC')))
            
            if ev.location:
                event.add("location", ev.location)
            
            cal.add_component(event)
    
    return cal
