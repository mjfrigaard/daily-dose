"""Pure, Shiny-free functions for loading and querying the workout history.

No ``shiny`` import belongs in this module — it must stay usable and
testable outside of a running app.
"""

from __future__ import annotations

import json
import random
from datetime import date
from importlib import resources
from typing import Any, cast

Workout = dict[str, Any]


def load_workouts() -> list[Workout]:
    """Load the bundled workout history.

    Returns:
        One dict per logged workout, each with ``date``, ``year``, ``kind``
        (``"text"`` or ``"image"``), ``done``, ``summary``, ``body_md``, and
        ``image_url`` keys.
    """
    data_text = resources.files("daily_dose.data").joinpath("workouts.json").read_text(
        encoding="utf-8"
    )
    return cast("list[Workout]", json.loads(data_text))


def random_workout(
    workouts: list[Workout], rng: random.Random | None = None
) -> Workout:
    """Pick one workout at random.

    Args:
        workouts: Candidate workouts, e.g. from `load_workouts`.
        rng: Optional `random.Random` instance for reproducible picks.

    Returns:
        A single randomly chosen workout dict.
    """
    chooser = rng or random
    return chooser.choice(workouts)


def on_this_day(workouts: list[Workout], today: date | None = None) -> list[Workout]:
    """Find every workout logged on this month/day, across all years.

    Args:
        workouts: Candidate workouts, e.g. from `load_workouts`.
        today: Date to match against; defaults to `date.today`.

    Returns:
        Matching workouts (0 or more), sorted most-recent year first.
    """
    target = today or date.today()
    matches = [
        w
        for w in workouts
        if int(w["date"][5:7]) == target.month and int(w["date"][8:10]) == target.day
    ]
    return sorted(matches, key=lambda w: w["date"], reverse=True)
