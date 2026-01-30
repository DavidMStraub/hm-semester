#!/usr/bin/env python3
"""
Example script showing how to create a calendar with weekly events.

This example demonstrates:
1. Creating lectures with deterministic UIDs for update tracking
2. Handling weekly and biweekly events
3. Updating room locations by incrementing sequence number
"""

from datetime import time
from hm_semester.agenda import WeeklyEvent, create_agenda
from hm_semester.semester import WINTER, SUMMER

# Define courses with course_id for deterministic UIDs
# Arguments: summary, course_id, weekday (0=Mon), start_time, end_time, location, biweekly (optional), start_week (optional)
events = [
    WeeklyEvent(
        summary="Algorithms",
        course_id="CS101",
        weekday=0,  # Monday
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 101",
    ),
    WeeklyEvent(
        summary="Database Lab",
        course_id="CS202",
        weekday=2,  # Wednesday
        start_time=time(13, 0),
        end_time=time(15, 0),
        location="Lab 305",
    ),
    WeeklyEvent(
        summary="Software Engineering Seminar",
        course_id="CS303",
        weekday=4,  # Friday
        start_time=time(14, 0),
        end_time=time(16, 0),
        location="Room 202",
        biweekly=True,
        start_week=1,
    ),
]

# Create the calendar for Summer Semester 2026
summer_calendar = create_agenda(events, 2026, "de", SUMMER)

# Write to a file
with open("summer_agenda_2026.ics", "wb") as f:
    f.write(summer_calendar.to_ical())

print("Created summer_agenda_2026.ics")

# Example: Update room location for all lectures
# Simply change the location and increment sequence number
print("\n--- Updating room location example ---")
events_updated = [
    WeeklyEvent(
        summary="Algorithms",
        course_id="CS101",  # Same course_id = same UID
        weekday=0,
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Room 999",  # Changed location!
        sequence=1,  # Increment sequence for updates
    ),
    WeeklyEvent(
        summary="Database Lab",
        course_id="CS202",
        weekday=2,
        start_time=time(13, 0),
        end_time=time(15, 0),
        location="Lab 305",  # Unchanged
        sequence=0,  # No change, same sequence
    ),
    WeeklyEvent(
        summary="Software Engineering Seminar",
        course_id="CS303",
        weekday=4,
        start_time=time(14, 0),
        end_time=time(16, 0),
        location="Room 202",  # Unchanged
        biweekly=True,
        start_week=1,
        sequence=0,
    ),
]

# Generate updated calendar
summer_calendar_updated = create_agenda(events_updated, 2026, "de", SUMMER)

# Write updated version
with open("summer_agenda_2026_updated.ics", "wb") as f:
    f.write(summer_calendar_updated.to_ical())

print("Created summer_agenda_2026_updated.ics")
print("Calendar apps will recognize the updated CS101 lectures (same UID, higher SEQUENCE)")
