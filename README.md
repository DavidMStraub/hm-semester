# hm-semester

A Python package for semester-related utilities specialized to [Hochschule München](https://www.hm.edu/) (HM).


## Usage

### As a CLI

After installing the package (e.g. with `pip install .`), you can generate a calendar file from the command line:

```bash
python -m hm_semester --year 2025 --semester winter --lang en
```

This will create a file like `winter_semester_2025_en.ics` in the current directory.

### As a Python module

You can also use the main function in your own scripts:

```python
from hm_semester.semester import generate_calendar

generate_calendar(2025, "winter", "en")
```

This will generate an `icalendar.Calendar` object that you can manipulate or save as needed.