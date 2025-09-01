from datetime import time

import icalendar

from hm_semester.agenda import WeeklyEvent, create_agenda
from hm_semester.semester import WINTER


def test_create_agenda_exdates():
    events = [
        WeeklyEvent(
            summary="Test Lecture",
            weekday=0,  # Monday
            start_time=time(10, 0),
            end_time=time(12, 0),
            location="Room 101",
        )
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    # Should be a Calendar
    assert isinstance(cal, icalendar.Calendar)
    # There should be at least one VEVENT
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 1
    event = vevents[0]
    # Check RRULE is present
    assert "RRULE" in event
    # Check EXDATEs are present (should be at least one for Christmas break)
    assert any(k == "EXDATE" for k, _ in event.property_items())
    # Check summary and location
    assert event.get("summary") == "Test Lecture"
    assert event.get("location") == "Room 101"
