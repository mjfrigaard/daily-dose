"""Entry point for Posit Connect Cloud, which expects `app.py` at the repo root.

Local development and testing use `daily_dose.app:app` directly (see README.md);
this file only exists so Connect Cloud's deploy step can find an app object here.
"""

from daily_dose.app import app

__all__ = ["app"]
