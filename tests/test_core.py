import random
from datetime import date

from daily_dose.core import Workout, on_this_day, random_workout

FIXTURE: list[Workout] = [
    {"date": "2020-06-15", "year": 2020, "kind": "text", "done": True,
     "summary": "a", "body_md": "a", "image_url": None},
    {"date": "2021-06-15", "year": 2021, "kind": "text", "done": True,
     "summary": "b", "body_md": "b", "image_url": None},
    {"date": "2021-06-16", "year": 2021, "kind": "image", "done": True,
     "summary": None, "body_md": None,
     "image_url": "/images/2021/2021-06-16.png"},
]


def test_random_workout_returns_member() -> None:
    result = random_workout(FIXTURE)
    assert result in FIXTURE


def test_random_workout_is_seedable() -> None:
    rng1 = random.Random(42)
    rng2 = random.Random(42)
    assert random_workout(FIXTURE, rng=rng1) == random_workout(FIXTURE, rng=rng2)


def test_on_this_day_matches_across_years() -> None:
    matches = on_this_day(FIXTURE, today=date(2026, 6, 15))
    assert [m["date"] for m in matches] == ["2021-06-15", "2020-06-15"]


def test_on_this_day_no_match_returns_empty() -> None:
    assert on_this_day(FIXTURE, today=date(2026, 1, 1)) == []


def test_on_this_day_single_match() -> None:
    matches = on_this_day(FIXTURE, today=date(2026, 6, 16))
    assert len(matches) == 1
    assert matches[0]["kind"] == "image"
