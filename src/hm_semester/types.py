from dataclasses import dataclass
from datetime import date


@dataclass
class SemesterInfo:
    start_date: date
    end_date: date
    vacation_start: date
    vacation_end: date
    breaks: dict[str, tuple[date, date]]
    label: str
