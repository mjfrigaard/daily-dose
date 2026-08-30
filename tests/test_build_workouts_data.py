import importlib.util
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "build_workouts_data.py"
)
spec = importlib.util.spec_from_file_location("build_workouts_data", SCRIPT_PATH)
assert spec and spec.loader
build_workouts_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_workouts_data)

parse_rmd = build_workouts_data.parse_rmd


def test_parse_rmd_splits_indented_date_heading(tmp_path: Path) -> None:
    """Regression test for the 2022-01-30/2022-01-29 bug: a date heading
    nested under the previous entry's list must become its own entry, not
    get swallowed into the entry above it."""
    rmd = tmp_path / "sample.Rmd"
    rmd.write_text(
        "### 2022-01-30\n\n"
        "- [x] 4x Rounds Of:\n"
        "  - 25x Push-Ups\n\n"
        "  ### 2022-01-29\n\n"
        "  - [x] work up to heavy power snatch\n"
    )
    entries = parse_rmd(rmd)
    assert [e["date"] for e in entries] == ["2022-01-30", "2022-01-29"]
    assert "2022-01-29" not in entries[0]["body_md"]


def test_parse_rmd_raises_on_unparseable_date_heading(tmp_path: Path) -> None:
    """A date-shaped heading that DATE_HEADER_RE won't match (wrong heading
    level here) must fail loudly instead of silently merging into the
    previous entry."""
    rmd = tmp_path / "sample.Rmd"
    rmd.write_text(
        "### 2022-01-30\n\n"
        "- [x] 4x Rounds Of:\n\n"
        "## 2022-01-29\n\n"
        "- [x] work up to heavy power snatch\n"
    )
    with pytest.raises(ValueError, match="2022-01-29"):
        parse_rmd(rmd)
