import subprocess
import sys


def test_main_cli(tmp_path):
    output_file = tmp_path / "winter_semester_2025_en.ics"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "hm_semester",
            "--year",
            "2025",
            "--semester",
            "winter",
            "--lang",
            "en",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "BEGIN:VCALENDAR" in content
    assert "Winter Semester" in content or "Wintersemester" in content
