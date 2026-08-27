"""Shiny UI helpers for rendering a workout as a card."""

from __future__ import annotations

from shiny import ui

from .core import Workout


def workout_card(workout: Workout) -> ui.Tag:
    """Render one workout as a `shiny.ui.card`.

    Args:
        workout: A single workout dict, e.g. from `daily_dose.core.random_workout`.

    Returns:
        A `shiny.ui.card` showing the workout's photo, or its markdown
        summary with an optional video link.
    """
    header = ui.card_header(workout["date"])
    if workout["kind"] == "image":
        img = ui.tags.img(src=workout["image_url"], style="max-width: 100%;")
        return ui.card(header, img)
    if workout["video_url"]:
        return ui.card(
            header,
            ui.markdown(workout["body_md"]),
            ui.a("Watch video", href=workout["video_url"], target="_blank"),
        )
    return ui.card(header, ui.markdown(workout["body_md"]))
