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
    assert isinstance(cal, icalendar.Calendar)
    # There should be at least one VEVENT
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 1
    event = vevents[0]
    assert "RRULE" in event
    assert "UID" in event
    # Check EXDATEs are present (should be at least one for Christmas break)
    assert any(k == "EXDATE" for k, _ in event.property_items())
    assert event.get("summary") == "Test Lecture"
    assert event.get("location") == "Room 101"


def test_create_agenda_biweekly():
    events = [
        WeeklyEvent(
            summary="Biweekly Seminar",
            weekday=2,  # Wednesday
            start_time=time(14, 0),
            end_time=time(16, 0),
            location="Room 202",
            biweekly=True,
            start_week=2,
        )
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    assert isinstance(cal, icalendar.Calendar)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 1
    event = vevents[0]
    # Check RRULE is present and interval is 2
    rrule = event.get("RRULE")
    assert rrule is not None
    assert rrule.get("INTERVAL") == 2
    # Check UID is present
    assert "UID" in event
    # Check summary and location
    assert event.get("summary") == "Biweekly Seminar"
    assert event.get("location") == "Room 202"
    # Check dtstart is a Wednesday
    assert event.get("dtstart").dt.weekday() == 2


def test_create_agenda_holiday_gaps():
    events = [
        WeeklyEvent(
            summary="Monday Lecture",
            weekday=0,  # Monday
            start_time=time(9, 0),
            end_time=time(10, 0),
            location="Room 101",
        ),
        WeeklyEvent(
            summary="Biweekly Seminar",
            weekday=2,  # Wednesday
            start_time=time(14, 0),
            end_time=time(16, 0),
            location="Room 202",
            biweekly=True,
            start_week=1,
        ),
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 2

    for event in vevents:
        raw_event = event.to_ical().decode()

        assert "UID" in event, f"No UID found for event {event.get('summary')}"
        assert (
            "EXDATE:" in raw_event
        ), f"No EXDATE found for event {event.get('summary')}"

        # Check if December or January dates are in the EXDATE values
        found_christmas = False
        if "EXDATE:2025122" in raw_event or "EXDATE:202601" in raw_event:
            found_christmas = True

        assert (
            found_christmas
        ), f"No Christmas EXDATE found for event {event.get('summary')}"

    assert vevents[0].get("summary") == "Monday Lecture"
    assert vevents[1].get("summary") == "Biweekly Seminar"
    assert vevents[0].get("location") == "Room 101"
    assert vevents[1].get("location") == "Room 202"
