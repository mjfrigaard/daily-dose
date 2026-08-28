"""Shiny UI helpers for rendering a workout as a card."""

from __future__ import annotations

from shiny import ui

from .core import Workout


def workout_card(workout: Workout) -> ui.Tag:
    """Render one workout as a `shiny.ui.card`.

    Args:
        workout: A single workout dict, e.g. from `daily_dose.core.random_workout`.

    Returns:
        A `shiny.ui.card` showing the workout's photo, or its markdown summary.
    """
    header = ui.card_header(workout["date"], class_="fw-semibold")
    if workout["kind"] == "image":
        img = ui.tags.img(
            src=workout["image_url"],
            class_="card-img-bottom border border-2",
            style="width: 100%;",
        )
        return ui.card(header, img)
    return ui.card(header, ui.card_body(ui.markdown(workout["body_md"])))
