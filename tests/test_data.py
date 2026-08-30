import re
from importlib import resources

from daily_dose.core import load_workouts

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_load_workouts_count() -> None:
    workouts = load_workouts()
    assert len(workouts) == 1001


def test_every_workout_has_a_valid_date_and_kind() -> None:
    for w in load_workouts():
        assert DATE_RE.match(w["date"])
        assert w["kind"] in ("text", "image")


def test_no_duplicate_dates() -> None:
    dates = [w["date"] for w in load_workouts()]
    assert len(dates) == len(set(dates))


def test_image_files_exist() -> None:
    www = resources.files("daily_dose").joinpath("www")
    for w in load_workouts():
        if w["kind"] == "image":
            rel = w["image_url"].lstrip("/")
            assert www.joinpath(rel).is_file(), w["image_url"]
