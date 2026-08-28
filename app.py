"""Entry point for Posit Connect Cloud, which expects `app.py` at the repo root.

Local development and testing use `daily_dose.app:app` directly (see README.md).
Connect Cloud's dependency resolver doesn't support installing this package via
`-e .` in requirements.txt (see requirements.txt), so `daily_dose` is never
actually installed there — this puts `src/` on `sys.path` instead so the import
below works anyway.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from daily_dose.app import app  # noqa: E402

__all__ = ["app"]
