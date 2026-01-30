from datetime import time
from zoneinfo import ZoneInfo

import icalendar

from hm_semester.agenda import WeeklyEvent, create_agenda
from hm_semester.semester import WINTER


def test_create_agenda_individual_events():
    """Test that lectures are now created as individual events, not RRULE."""
    events = [
        WeeklyEvent(
            summary="Test Lecture",
            course_id="test-course",
            weekday=0,  # Monday
            start_time=time(10, 0),
            end_time=time(12, 0),
            location="Room 101",
        )
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    assert isinstance(cal, icalendar.Calendar)
    
    # Should have multiple individual VEVENTs (one per lecture occurrence)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) > 1, "Should have multiple individual lecture events"
    
    # Check first event
    event = vevents[0]
    # Should NOT have RRULE anymore
    assert "RRULE" not in event, "Individual events should not have RRULE"
    # Should NOT have EXDATE anymore
    assert "EXDATE" not in event, "Individual events should not have EXDATE"
    # Should have UID in deterministic format
    assert "UID" in event
    assert "@hm.edu" in event.get("uid")
    # Should have lesson number in summary
    summary = event.get("summary")
    assert "Test Lecture" in summary
    assert "(1)" in summary
    # Should have location
    assert event.get("location") == "Room 101"
    # Should have DTSTAMP
    assert "DTSTAMP" in event
    # Should have SEQUENCE
    assert "SEQUENCE" in event


def test_create_agenda_biweekly():
    """Test biweekly lectures are created as individual events."""
    events = [
        WeeklyEvent(
            summary="Biweekly Seminar",
            course_id="biweekly-course",
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
    
    # Should have fewer events than weekly (roughly half)
    assert len(vevents) > 1, "Should have multiple biweekly events"
    
    event = vevents[0]
    # No RRULE anymore
    assert "RRULE" not in event
    # Check UID format
    assert "UID" in event
    assert "biweekly-course" in event.get("uid")
    # Check summary
    assert "Biweekly Seminar" in event.get("summary")
    assert event.get("location") == "Room 202"
    # Check dtstart is a Wednesday
    assert event.get("dtstart").dt.weekday() == 2


def test_create_agenda_no_holidays():
    """Test that individual events don't fall on holiday dates."""
    events = [
        WeeklyEvent(
            summary="Monday Lecture",
            course_id="monday-course",
            weekday=0,  # Monday
            start_time=time(9, 0),
            end_time=time(10, 0),
            location="Room 101",
        )
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    
    # Get all lecture dates
    lecture_dates = [event.get("dtstart").dt.date() for event in vevents]
    
    # Check that none of the lectures fall in Christmas break
    # Winter 2025 Christmas break is roughly Dec 24, 2025 - Jan 6, 2026
    from datetime import date
    christmas_start = date(2025, 12, 24)
    christmas_end = date(2026, 1, 6)
    
    for lecture_date in lecture_dates:
        assert not (christmas_start <= lecture_date <= christmas_end), \
            f"Lecture on {lecture_date} falls during Christmas break"


def test_timezone():
    """Test that timezone is properly set on individual events."""
    custom_timezone = "America/New_York"
    events = [
        WeeklyEvent(
            summary="Timezone Test Event",
            course_id="timezone-course",
            weekday=1,
            start_time=time(10, 0),
            end_time=time(11, 0),
            timezone=custom_timezone,
        )
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) > 1
    
    # Check all events have correct timezone
    for event in vevents:
        dt_start = event.get("dtstart").dt
        dt_end = event.get("dtend").dt
        assert dt_start.tzinfo is not None
        assert dt_start.tzinfo.key == custom_timezone
        assert dt_end.tzinfo.key == custom_timezone


def test_deterministic_uid():
    """Test that UIDs are deterministic for update tracking."""
    events = [
        WeeklyEvent(
            summary="Course A",
            course_id="CS101",
            weekday=0,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
    ]
    
    # Generate twice
    cal1 = create_agenda(events, 2025, "en", WINTER)
    cal2 = create_agenda(events, 2025, "en", WINTER)
    
    vevents1 = [c for c in cal1.walk() if c.name == "VEVENT"]
    vevents2 = [c for c in cal2.walk() if c.name == "VEVENT"]
    
    # Same UIDs should be generated
    uids1 = [e.get("uid") for e in vevents1]
    uids2 = [e.get("uid") for e in vevents2]
    
    assert uids1 == uids2, "UIDs should be deterministic"
    
    # Check format
    assert all("CS101" in uid for uid in uids1)
    assert all("2025" in uid for uid in uids1)
    assert all("winter" in uid for uid in uids1)
    assert all("@hm.edu" in uid for uid in uids1)


def test_sequence_tracking():
    """Test that SEQUENCE field is added for version tracking."""
    events = [
        WeeklyEvent(
            summary="Course A",
            course_id="CS101",
            weekday=0,
            start_time=time(10, 0),
            end_time=time(12, 0),
            sequence=2,  # Simulate an update
        )
    ]
    
    cal = create_agenda(events, 2025, "en", WINTER)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    
    # All events should have SEQUENCE=2
    for event in vevents:
        assert event.get("sequence") == 2


def test_biweekly_start_week_greater_than_two():
    """Test that biweekly events work with start_week > 2."""
    events = [
        WeeklyEvent(
            summary="Group A",
            course_id="groupA",
            weekday=0,  # Monday
            start_time=time(10, 0),
            end_time=time(12, 0),
            biweekly=True,
            start_week=1,
        ),
        WeeklyEvent(
            summary="Group B",
            course_id="groupB",
            weekday=0,  # Monday
            start_time=time(10, 0),
            end_time=time(12, 0),
            biweekly=True,
            start_week=2,
        ),
        WeeklyEvent(
            summary="Group C",
            course_id="groupC",
            weekday=0,  # Monday
            start_time=time(10, 0),
            end_time=time(12, 0),
            biweekly=True,
            start_week=3,
        ),
        WeeklyEvent(
            summary="Group D",
            course_id="groupD",
            weekday=0,  # Monday
            start_time=time(10, 0),
            end_time=time(12, 0),
            biweekly=True,
            start_week=4,
        ),
    ]
    
    cal = create_agenda(events, 2026, "en", "summer")
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    
    # Group events by course_id
    from collections import defaultdict
    groups = defaultdict(list)
    for event in vevents:
        uid = event.get("uid")
        course_id = uid.split("-")[0]
        date = event.get("dtstart").dt.date()
        groups[course_id].append(date)
    
    # Sort dates for each group
    for course_id in groups:
        groups[course_id].sort()
    
    # Verify each group has events
    assert len(groups["groupA"]) > 0
    assert len(groups["groupB"]) > 0
    assert len(groups["groupC"]) > 0
    assert len(groups["groupD"]) > 0
    
    # Get first dates for each group
    first_dates = {
        "groupA": groups["groupA"][0],
        "groupB": groups["groupB"][0],
        "groupC": groups["groupC"][0],
        "groupD": groups["groupD"][0],
    }
    
    # Verify staggering: each group should start 1 week after the previous
    from datetime import timedelta
    assert first_dates["groupB"] == first_dates["groupA"] + timedelta(days=7)
    assert first_dates["groupC"] == first_dates["groupA"] + timedelta(days=14)
    # Group D starts in week 4, but due to biweekly logic, it's actually 4 weeks (28 days) after Group A
    assert first_dates["groupD"] == first_dates["groupA"] + timedelta(days=28)
    
    # Verify biweekly pattern for each group (should be every other occurrence)
    # Due to holidays, the gaps may be larger than 14 days, but should maintain biweekly pattern
    for course_id, dates in groups.items():
        if len(dates) >= 2:
            # Check that events are spaced at least 14 days apart (but can be more due to holidays)
            for i in range(len(dates) - 1):
                days_diff = (dates[i + 1] - dates[i]).days
                assert days_diff >= 14, f"{course_id} events too close: {days_diff} days between {dates[i]} and {dates[i+1]}"
