"""App theme: a bslib preset plus Google Fonts for headings and body text."""

from __future__ import annotations

from shiny.ui import Theme, tags

GOOGLE_FONTS_LINKS = (
    tags.link(rel="preconnect", href="https://fonts.googleapis.com"),
    tags.link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
    tags.link(
        rel="stylesheet",
        href=(
            "https://fonts.googleapis.com/css2?"
            "family=Poppins:wght@600;700"
            "&family=Inter:wght@400;500;600"
            "&display=swap"
        ),
    ),
)

# Bootswatch's "pulse" $primary, kept as the accent on a dark base since dark
# presets (darkly, cyborg, ...) each ship their own default accent color.
PULSE_PURPLE = "#593196"

theme = Theme(preset="darkly").add_defaults(
    primary=PULSE_PURPLE,
    font_family_base="'Inter', system-ui, sans-serif",
    headings_font_family="'Poppins', system-ui, sans-serif",
    headings_font_weight="700",
)
