"""Shiny Core app: pick a random workout, or see workouts from this day."""

from __future__ import annotations

from pathlib import Path

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

from .core import Workout, load_workouts, on_this_day, random_workout
from .workout_module import workout_card

WORKOUTS: list[Workout] = load_workouts()
STATIC_ASSETS = Path(__file__).parent / "www"

app_ui = ui.page_fluid(
    ui.h2("The Daily Dose"),
    ui.layout_columns(
        ui.input_action_button("random_btn", "🎲 Random Workout", class_="btn-primary"),
        ui.input_action_button("today_btn", "📅 On This Day", class_="btn-secondary"),
        col_widths=(6, 6),
    ),
    ui.output_ui("results"),
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
        return ui.div(*[workout_card(w) for w in workouts])


app = App(app_ui, server, static_assets=STATIC_ASSETS)
