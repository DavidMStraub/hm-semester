#!/usr/bin/env python3
"""
Example script showing how to create a calendar with weekly events.
"""

from datetime import time
from hm_semester.agenda import WeeklyEvent, create_agenda
from hm_semester.semester import WINTER, SUMMER

# arguments: title, weekday (0=Mon), start_time, end_time, location, biweekly (optional), start_week (optional)
events = [
    WeeklyEvent("Monday Lecture", 0, time(9, 0), time(10, 0), "Room 101"),
    WeeklyEvent("Wednesday Lab", 2, time(13, 0), time(15, 0), "Lab 305"),
    WeeklyEvent("Biweekly Seminar", 4, time(14, 0), time(16, 0), "Room 202", True, 1),
]

# Create the calendar for Winter Semester 2025
winter_calendar = create_agenda(events, 2025, "de", WINTER)

# Write to a file
with open("winter_agenda_2025.ics", "wb") as f:
    f.write(winter_calendar.to_ical())
