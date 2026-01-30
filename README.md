# hm-semester

A Python package for generating ICS calendar files for Hochschule München (HM) semesters. Create calendars with semester dates, breaks, holidays, and weekly/biweekly lecture schedules.

## Features

- **Semester Calendar**: Generate calendars with semester start/end dates and breaks (Christmas, Easter, Pentecost)
- **Lecture Agenda**: Create individual lecture events with holiday-aware scheduling
- **Biweekly Support**: Handle biweekly lectures that maintain alternating patterns even when holidays interrupt
- **Update Tracking**: Deterministic UIDs and SEQUENCE numbers for calendar updates
- **Multi-language**: Support for German and English labels


## Usage

### Semester Calendar (Holidays & Breaks)

Generate a calendar with semester dates and break periods.

#### CLI

```bash
python -m hm_semester --year 2025 --semester winter --lang en
```

This creates `winter_semester_2025_en.ics` with:
- Semester start and end dates
- Christmas break (Winter semester)
- Easter and Pentecost breaks (Summer semester)

#### Python API

```python
from hm_semester.semester import generate_calendar

cal = generate_calendar(2025, "winter", "en")
with open("semester.ics", "wb") as f:
    f.write(cal.to_ical())
```

### Lecture Agenda

Generate individual lecture events with holiday-aware scheduling.

#### Basic Example

```python
from datetime import time
from hm_semester.agenda import WeeklyEvent, create_agenda

events = [
    WeeklyEvent(
        summary="Algorithms",
        course_id="CS101",
        weekday=0,  # Monday
        start_time=time(9, 0),
        end_time=time(11, 0),
        location="Room 101",
    ),
    WeeklyEvent(
        summary="Database Systems",
        course_id="CS202",
        weekday=2,  # Wednesday
        start_time=time(14, 0),
        end_time=time(16, 0),
        location="Lab 305",
        biweekly=True,  # Every 2 weeks
        start_week=1,
    ),
]

cal = create_agenda(events, 2026, "en", "summer")
with open("lectures.ics", "wb") as f:
    f.write(cal.to_ical())
```

#### WeeklyEvent Parameters

- `summary` (str): Event title
- `course_id` (str): Course identifier for deterministic UID generation
- `weekday` (int): Day of week (0=Monday, 6=Sunday)
- `start_time` (time): Lecture start time
- `end_time` (time): Lecture end time
- `location` (str, optional): Room or building
- `biweekly` (bool, optional): If True, event occurs every 2 weeks
- `start_week` (int, optional): For biweekly, which week to start (1, 2, 3, ...)
- `timezone` (str, optional): Timezone name (default: "Europe/Berlin")
- `sequence` (int, optional): Version number for updates (default: 0)

#### Holiday-Aware Scheduling

Lectures automatically skip semester breaks:
- Individual events are generated (no RRULE)
- Holidays are excluded from the schedule
- Biweekly lectures maintain alternating pattern even when holidays interrupt
  - Example: If a biweekly lecture would be in week 7 (holiday), it shifts to week 8

#### Biweekly Patterns

Use `start_week` to stagger multiple biweekly groups:

```python
# Four groups meeting every 2 weeks, staggered by 1 week
groups = [
    WeeklyEvent("Group A", "grpA", 0, time(10, 0), time(12, 0), 
                biweekly=True, start_week=1),
    WeeklyEvent("Group B", "grpB", 0, time(10, 0), time(12, 0), 
                biweekly=True, start_week=2),
    WeeklyEvent("Group C", "grpC", 0, time(10, 0), time(12, 0), 
                biweekly=True, start_week=3),
    WeeklyEvent("Group D", "grpD", 0, time(10, 0), time(12, 0), 
                biweekly=True, start_week=4),
]
```

### Updating Calendars

When room locations or times change, increment the `sequence` parameter:

```python
# Initial calendar
events = [
    WeeklyEvent("Algorithms", "CS101", 0, time(9, 0), time(11, 0), 
                location="Room 101", sequence=0),
]
cal = create_agenda(events, 2026, "en", "summer")

# Later: room changed
events[0].location = "Room 999"
events[0].sequence = 1
updated_cal = create_agenda(events, 2026, "en", "summer")
```

**For Thunderbird/local calendar apps**: Delete the old calendar and import the new one.

**For CalDAV/subscribed calendars**: Events with the same UID and higher SEQUENCE are automatically updated.

## Examples

See [examples/create_agenda_example.py](examples/create_agenda_example.py) for a complete example.

## Output Format

- Each lecture gets a unique event with format: `"Course Name (1)"`, `"Course Name (2)"`, etc.
- UIDs are deterministic: `{course_id}-{year}-{semester}-lesson-{number}@hm.edu`
- VTIMEZONE components are included for proper timezone handling
- SEQUENCE field tracks version numbers for updates

## Installation

### From PyPI

```bash
pip install hm-semester
```

### From source

```bash
git clone https://github.com/DavidMStraub/hm-semester.git
cd hm-semester
pip install .
```

## Development

Run tests:
```bash
pytest tests/
```

### Release Process

This package uses GitHub Actions for automated PyPI releases:

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a new release on GitHub
4. The workflow automatically builds and publishes to PyPI and TestPyPI

The workflow uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no API tokens needed). Configure trusted publishers:
- PyPI: Add GitHub repository as trusted publisher at https://pypi.org/manage/account/publishing/
- TestPyPI: Add GitHub repository at https://test.pypi.org/manage/account/publishing/
