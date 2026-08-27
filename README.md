# daily-dose

A Shiny for Python app for browsing a personal workout log (2020-2024), converted from
the original R Markdown site. Two features:

- **Random Workout** — pick one workout at random from the whole history.
- **On This Day** — show every workout logged on today's month/day, across all years.

Workouts are stored as either typed markdown (with an optional video link) or a photo
of the day's workout board/log.

## Install

```bash
uv venv
uv pip install -e ".[dev]"
```

## Run

```bash
shiny run daily_dose.app:app --reload
```

## Test

```bash
uv run pytest
uv run ruff check src tests
uv run mypy src
```

## Docs

Docs are built with [great-docs](https://posit-dev.github.io/great-docs/) and organized
by [Diátaxis](https://diataxis.fr/): this README is the homepage, `tutorials/` is a
guided first run, `how-to/` has task recipes (regenerating the workout data, updating
screenshots, rebuilding the site), `explanation/` covers design decisions, and
`reference/` is generated from `daily_dose.core`'s docstrings.

```bash
great-docs build
```
