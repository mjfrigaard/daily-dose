"""Shiny Core app: pick a random workout, or see workouts from this day."""

from __future__ import annotations

from pathlib import Path

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

from .core import Workout, load_workouts, on_this_day, random_workout
from .theme import GOOGLE_FONTS_LINKS, theme
from .workout_module import workout_card

WORKOUTS: list[Workout] = load_workouts()
STATIC_ASSETS = Path(__file__).parent / "www"

app_ui = ui.page_fluid(
    ui.tags.head(*GOOGLE_FONTS_LINKS),
    ui.div(
        ui.div(
            ui.h2("The Daily Dose", class_="fw-bold"),
            ui.p(
                "A random pick, or a look back at today, any year.",
                class_="text-muted",
            ),
            class_="text-center mb-4",
        ),
        ui.layout_columns(
            ui.input_action_button(
                "random_btn", "🎲 Random Workout", class_="btn-primary btn-lg"
            ),
            ui.input_action_button(
                "today_btn", "📅 On This Day", class_="btn-secondary btn-lg"
            ),
            col_widths=(6, 6),
        ),
        ui.output_ui("results"),
        style="max-width: 720px; margin: 0 auto; padding: 2.5rem 1rem;",
    ),
    theme=theme,
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    shown: reactive.Value[list[Workout] | None] = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.random_btn)
    def _() -> None:
        shown.set([random_workout(WORKOUTS)])

    @reactive.effect
    @reactive.event(input.today_btn)
    def _() -> None:
        shown.set(on_this_day(WORKOUTS))

    @render.ui
    def results() -> ui.Tag:
        workouts = shown()
        if workouts is None:
            return ui.p("Click a button above to see a workout.", class_="text-muted")
        if not workouts:
            msg = "No workouts logged on this day in past years."
            return ui.p(msg, class_="text-muted")
        cards = [workout_card(w) for w in workouts]
        return ui.div(*cards, class_="d-flex flex-column gap-3 mt-3")


app = App(app_ui, server, static_assets=STATIC_ASSETS)
