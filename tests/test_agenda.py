from collections import defaultdict
from datetime import date, time, timedelta
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
    christmas_start = date(2025, 12, 24)
    christmas_end = date(2026, 1, 6)
    
    for lecture_date in lecture_dates:
        assert not (christmas_start <= lecture_date <= christmas_end), \
            f"Lecture on {lecture_date} falls during Christmas break"


def test_timezone():
    """Test that events are converted to UTC."""
    events = [
        WeeklyEvent(
            summary="Timezone Test Event",
            course_id="timezone-course",
            weekday=1,
            start_time=time(10, 0),
            end_time=time(11, 0),
            timezone="Europe/Berlin",
        )
    ]
    cal = create_agenda(events, 2025, "en", WINTER)
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) > 1
    
    # Check all events are in UTC
    for event in vevents:
        dt_start = event.get("dtstart").dt
        dt_end = event.get("dtend").dt
        assert dt_start.tzinfo is not None
        assert dt_end.tzinfo is not None
        # Should be UTC
        assert dt_start.tzinfo.key == "UTC"
        assert dt_end.tzinfo.key == "UTC"


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
    
    # Verify staggering: groups should be separated by weeks
    # The current implementation means:
    # - Group A (start_week=1): weeks 1, 3, 5, 7, 9...
    # - Group B (start_week=2): weeks 2, 4, 6, 8, 10...
    # - Group C (start_week=3): weeks 3, 5, 7, 9, 11...
    # - Group D (start_week=4): weeks 4, 6, 8, 10, 12...
    # 
    # Note: Groups A and C overlap (both on odd weeks), and B and D overlap (both on even weeks)
    # This is the current behavior when using start_week for biweekly scheduling
    
    # All groups should have different first dates
    assert len(set(first_dates.values())) == 4, "Each group should start on a different date"
    
    # Verify that first occurrences are in the right weeks
    # Note: holidays may shift some first occurrences
    assert first_dates["groupB"] >= first_dates["groupA"] + timedelta(days=7)
    assert first_dates["groupC"] >= first_dates["groupA"] + timedelta(days=14)
    # Group D might skip week 4 if it's a holiday, so just check it's after Group C
    assert first_dates["groupD"] > first_dates["groupC"]
    
    # Verify biweekly pattern for each group (should be every other occurrence)
    # Due to holidays, the gaps may be larger than 14 days, but should maintain biweekly pattern
    for course_id, dates in groups.items():
        if len(dates) >= 2:
            # Check that events are spaced at least 14 days apart (but can be more due to holidays)
            for i in range(len(dates) - 1):
                days_diff = (dates[i + 1] - dates[i]).days
                assert days_diff >= 14, f"{course_id} events too close: {days_diff} days between {dates[i]} and {dates[i+1]}"


def test_biweekly_holiday_shifts_to_next_week():
    """Test that when a biweekly event's scheduled week is a holiday, it shifts to the next available week."""
    # Summer 2026 has Easter holiday on week 3 Thursday (April 2-7)
    # Group starting in week 3 should shift to week 4, then continue biweekly from there
    events = [
        WeeklyEvent(
            summary="Group starting week 3",
            course_id="week3-group",
            weekday=3,  # Thursday
            start_time=time(15, 0),
            end_time=time(16, 30),
            biweekly=True,
            start_week=3,
        )
    ]
    
    cal = create_agenda(events, 2026, "en", "summer")
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    
    dates = sorted([event.get("dtstart").dt.date() for event in vevents])
    
    # Week 3 Thursday is April 2 (holiday), so should shift to week 4 (April 9)
    # Then continue biweekly: week 4, 6, 8, 10...

    # First occurrence should be April 9 (week 4), not skipping to April 16 (week 5)
    assert dates[0] == date(2026, 4, 9), f"Expected first date to be April 9 (shifted from holiday), got {dates[0]}"

    # Second occurrence should be April 23 (two weeks after April 9)
    assert dates[1] == date(2026, 4, 23), f"Expected second date to be April 23, got {dates[1]}"

    # Gaps are normally 14 days; a single-day public holiday landing on a biweekly
    # slot causes the next occurrence to shift by one extra week → 21-day gap.
    for i in range(len(dates) - 1):
        days_diff = (dates[i + 1] - dates[i]).days
        assert days_diff in (14, 21), (
            f"Expected 14 or 21 days between occurrences, "
            f"got {days_diff} between {dates[i]} and {dates[i+1]}"
        )


# ---------------------------------------------------------------------------
# Public holiday skipping
# ---------------------------------------------------------------------------


def _thu_summer(year: int) -> set[date]:
    """Helper: lecture dates for a weekly Thursday course in the given summer semester."""
    events = [
        WeeklyEvent(
            summary="Thu Lecture",
            course_id="thu",
            weekday=3,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )
    ]
    cal = create_agenda(events, year, "de", "summer")
    return {ev.get("dtstart").dt.date() for ev in cal.walk() if ev.name == "VEVENT"}


def _weekday_summer(weekday: int, year: int) -> set[date]:
    """Helper: lecture dates for a weekly course on the given weekday in summer semester."""
    events = [
        WeeklyEvent(
            summary="Lecture",
            course_id="lec",
            weekday=weekday,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )
    ]
    cal = create_agenda(events, year, "de", "summer")
    return {ev.get("dtstart").dt.date() for ev in cal.walk() if ev.name == "VEVENT"}


def _weekday_winter(weekday: int, year: int) -> set[date]:
    """Helper: lecture dates for a weekly course on the given weekday in winter semester."""
    events = [
        WeeklyEvent(
            summary="Lecture",
            course_id="lec",
            weekday=weekday,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )
    ]
    cal = create_agenda(events, year, "de", "winter")
    return {ev.get("dtstart").dt.date() for ev in cal.walk() if ev.name == "VEVENT"}


# --- Summer semester 2026 public holidays ---

def test_agenda_skips_christi_himmelfahrt_2026():
    """Christi Himmelfahrt 2026 = 14 May (Thursday) must have no lecture."""
    assert date(2026, 5, 14) not in _thu_summer(2026)


def test_agenda_skips_fronleichnam_2026():
    """Fronleichnam 2026 = 4 June (Thursday) must have no lecture."""
    assert date(2026, 6, 4) not in _thu_summer(2026)


def test_agenda_skips_tag_der_arbeit_2026():
    """1. Mai 2026 is a Friday — no Friday lecture."""
    assert date(2026, 5, 1) not in _weekday_summer(4, 2026)


def test_agenda_skips_pfingstmontag_2026():
    """Pfingstmontag 2026 = 25 May (Monday) must have no lecture."""
    assert date(2026, 5, 25) not in _weekday_summer(0, 2026)


def test_agenda_skips_karfreitag_2026():
    """Karfreitag 2026 = 3 April (Friday) must have no lecture."""
    assert date(2026, 4, 3) not in _weekday_summer(4, 2026)


def test_agenda_skips_ostermontag_2026():
    """Ostermontag 2026 = 6 April (Monday) must have no lecture."""
    assert date(2026, 4, 6) not in _weekday_summer(0, 2026)


# --- Winter semester 2025 public holidays ---

def test_agenda_skips_tag_der_deutschen_einheit_2025():
    """Tag der Deutschen Einheit 2025 = 3 October (Friday) must have no lecture."""
    assert date(2025, 10, 3) not in _weekday_winter(4, 2025)


def test_agenda_skips_allerheiligen_2025():
    """Allerheiligen 2025 = 1 November (Saturday) — falls on weekend, no lecture anyway.
    Use 2026 where it's a Sunday, and 2024 where it falls on a Friday to properly test."""
    # WS 2024: Allerheiligen = 1 Nov 2024 (Friday)
    assert date(2024, 11, 1) not in _weekday_winter(4, 2024)


def test_agenda_skips_christmas_eve_winter():
    """No Monday lecture on 24 December during Christmas break."""
    # WS 2025: 24 Dec 2025 is a Wednesday
    assert date(2025, 12, 24) not in _weekday_winter(2, 2025)


def test_agenda_skips_heilige_drei_koenige_winter():
    """Heilige Drei Könige (6 Jan) is a Bavarian holiday — should be skipped in WS.
    In WS 2025 it falls on a Tuesday (6 Jan 2026)."""
    assert date(2026, 1, 6) not in _weekday_winter(1, 2025)
