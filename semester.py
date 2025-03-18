from datetime import date, timedelta
import calendar
from icalendar import Calendar, Event

def adjust_start_date(start_date):
    """ Adjust start date to the next Monday if it falls on a Friday, Saturday, or Sunday. """
    if start_date.weekday() in [4, 5, 6]:
        return start_date + timedelta(days=(7 - start_date.weekday()))
    return start_date

def adjust_end_date(end_date):
    """ Adjust end date to the previous Friday if it falls on a Saturday, Sunday, or Monday. """
    if end_date.weekday() in [5, 6, 0]:
        return end_date - timedelta(days=(end_date.weekday() - 4) % 7)
    return end_date

def get_christmas_break(year):
    """ Determine the Christmas break period. """
    start = date(year, 12, 24)
    if start.weekday() in [6, 0, 1]:  # Sunday, Monday, Tuesday
        start -= timedelta(days=(start.weekday() - 5) % 7)
    end = date(year + 1, 1, 6)
    if end.weekday() in [4, 5, 6]:  # Friday, Saturday, Sunday
        end += timedelta(days=(7 - end.weekday()))
    return start, end

def get_easter_break(year):
    """ Determine the Easter break period from Maundy Thursday to the following Tuesday. """
    easter_sunday = get_easter_sunday(year)
    start = easter_sunday - timedelta(days=3)  # Maundy Thursday
    end = easter_sunday + timedelta(days=2)    # Tuesday after Easter
    return start, end

def get_pentecost_break(year):
    """ Determine the Pentecost break from the Friday before to the following Tuesday. """
    pentecost_sunday = get_easter_sunday(year) + timedelta(days=49)
    start = pentecost_sunday - timedelta(days=2)  # Friday before Pentecost
    end = pentecost_sunday + timedelta(days=2)    # Tuesday after Pentecost
    return start, end

def get_easter_sunday(year):
    """ Compute the date of Easter Sunday using the Meeus/Jones/Butcher algorithm. """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def generate_calendar(year, semester):
    """ Generate an iCalendar file for the given semester and year. """
    cal = Calendar()
    
    if semester == "winter":
        start_date = adjust_start_date(date(year, 10, 1))
        end_date = adjust_end_date(date(year + 1, 1, 25))
        break_start, break_end = get_christmas_break(year)
        break_label = "Christmas Break"
        vacation_start = end_date + timedelta(days=1)
        vacation_end = date(year + 1, 3, 14)
    else:
        start_date = adjust_start_date(date(year, 3, 15))
        end_date = adjust_end_date(date(year, 7, 10))
        easter_start, easter_end = get_easter_break(year)
        pentecost_start, pentecost_end = get_pentecost_break(year)
        break_start, break_end = None, None
        vacation_start = end_date + timedelta(days=1)
        vacation_end = date(year, 9, 30)
    
    # Add lecture period
    event = Event()
    event.add("summary", "Lecture Period")
    event.add("dtstart", start_date)
    event.add("dtend", end_date)
    cal.add_component(event)
    
    # Add semester break
    event = Event()
    event.add("summary", "Semester Break")
    event.add("dtstart", vacation_start)
    event.add("dtend", vacation_end)
    cal.add_component(event)
    
    # Add holiday breaks
    if semester == "winter":
        event = Event()
        event.add("summary", break_label)
        event.add("dtstart", break_start)
        event.add("dtend", break_end)
        cal.add_component(event)
    else:
        for start, end, label in [(easter_start, easter_end, "Easter Break"), (pentecost_start, pentecost_end, "Pentecost Break")]:
            event = Event()
            event.add("summary", label)
            event.add("dtstart", start)
            event.add("dtend", end)
            cal.add_component(event)
    
    # Write to file
    filename = f"{semester}_semester_{year}.ics"
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    print(f"Calendar saved as {filename}")

# Example usage
generate_calendar(2025, "winter")
generate_calendar(2025, "summer")
