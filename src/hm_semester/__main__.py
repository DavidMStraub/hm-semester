import click
from hm_semester.semester import generate_calendar
from hm_semester.const import WINTER, SUMMER

@click.command()
@click.option('--year', required=True, type=int, help='Year of the semester')
@click.option('--semester', required=True, type=click.Choice([WINTER, SUMMER]), help='Semester (winter or summer)')
@click.option('--lang', default='en', type=click.Choice(['en', 'de']), help='Language (en or de)')
def main(year, semester, lang):
    """Generate a semester calendar and write it to an .ics file."""
    cal = generate_calendar(year, semester, lang)

    # Write to file
    filename = f"{semester}_semester_{year}_{lang}.ics"
    with open(filename, "wb") as f:
        f.write(cal.to_ical())
    print(f"Calendar saved as {filename}")


if __name__ == '__main__':
    main()
