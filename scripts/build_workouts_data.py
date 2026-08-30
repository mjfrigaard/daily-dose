"""One-off converter: legacy Rmd workout logs + dated images -> workouts.json.

Not shipped with the package; run manually whenever the source Rmd/images
change:

    uv run python scripts/build_workouts_data.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageOps

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_IMAGE_DIM = 1600
JPEG_QUALITY = 82
RMD_FILES = ["index.Rmd", "20-wo.Rmd", "21-wo.Rmd", "22-wo.Rmd", "23-wo.Rmd"]
RMD_DIR = REPO_ROOT / "scripts" / "_rmd_src"
IMAGES_DIR = REPO_ROOT / "images"
WWW_IMAGES_DIR = REPO_ROOT / "src" / "daily_dose" / "www" / "images"
DATA_PATH = REPO_ROOT / "src" / "daily_dose" / "data" / "workouts.json"

DATE_HEADER_RE = re.compile(r"^\s*###\s+(\d{4}-\d{2}-\d{2})\s*$")
# Looser than DATE_HEADER_RE: catches anything date-shaped that looks like a
# heading (wrong heading level, trailing text, ...) so parse_rmd can fail
# loudly instead of silently merging it into the previous entry's body.
LOOSE_DATE_HEADER_RE = re.compile(r"^\s*#+\s*\d{4}-\d{2}-\d{2}")
SECTION_BREAK_RE = re.compile(r"^#{1,2}\s+")
CHECKBOX_RE = re.compile(r"^-\s*\[( |x)\]\s*")
# The Vimeo account these pointed at is gone, so every video link is now dead.
# Unwrap `[text](vimeo-url)` down to plain `text` wherever it appears in an entry.
VIMEO_LINK_RE = re.compile(r"\[([^\]]*)\]\(https?://(?:www\.)?vimeo\.com/[^)]+\)")
# A few entries reference Vimeo as a bare URL instead (e.g. "Throwback to: <url>").
BARE_VIMEO_RE = re.compile(r"https?://(?:www\.)?vimeo\.com/\S+")


def clean_vimeo(line: str) -> str | None:
    """Strip Vimeo links/URLs from a line; drop the line if that leaves only
    a dangling label (e.g. "Throwback to:") with nothing after it."""
    line = VIMEO_LINK_RE.sub(r"\1", line)
    if BARE_VIMEO_RE.search(line):
        line = BARE_VIMEO_RE.sub("", line).rstrip()
        if not line or line.endswith((":", "-", "*")):
            return None
    return line


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def parse_rmd(path: Path) -> list[dict]:
    text = strip_html_comments(path.read_text(encoding="utf-8"))
    lines = text.splitlines()

    entries: list[dict] = []
    current_date: str | None = None
    body_lines: list[str] = []

    def flush() -> None:
        if current_date is None:
            return
        cleaned = (clean_vimeo(ln) for ln in body_lines)
        cleaned_lines = [ln for ln in cleaned if ln is not None]
        body = "\n".join(cleaned_lines).strip("\n")
        first_line = next((ln for ln in cleaned_lines if ln.strip()), "")
        checkbox_match = CHECKBOX_RE.match(first_line.strip())
        done = checkbox_match.group(1) == "x" if checkbox_match else True
        summary = (
            first_line.strip()[checkbox_match.end() :].strip()
            if checkbox_match
            else first_line.strip()
        )
        entries.append(
            {
                "date": current_date,
                "year": int(current_date[:4]),
                "kind": "text",
                "done": done,
                "summary": summary,
                "body_md": body,
                "image_url": None,
                "source_file": path.name,
            }
        )

    for line in lines:
        date_match = DATE_HEADER_RE.match(line)
        if date_match:
            flush()
            current_date = date_match.group(1)
            body_lines = []
            continue
        if LOOSE_DATE_HEADER_RE.match(line):
            raise ValueError(
                f"{path.name}: date-shaped heading won't be parsed as its "
                f"own entry, it'll be swallowed into the previous one: "
                f"{line!r}"
            )
        if SECTION_BREAK_RE.match(line) and current_date is not None:
            flush()
            current_date = None
            body_lines = []
            continue
        if current_date is not None:
            body_lines.append(line)

    flush()
    return entries


def collect_image_entries() -> list[dict]:
    """Find date-named workout photos. Does not copy files yet — only
    entries that survive dedupe_by_date() get copied, in copy_images_for()."""
    entries: list[dict] = []
    for src in sorted(IMAGES_DIR.rglob("*")):
        if not src.is_file() or src.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        date_str = src.stem
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            continue
        year_dir = src.parent.name
        entries.append(
            {
                "date": date_str,
                "year": int(date_str[:4]),
                "kind": "image",
                "done": True,
                "summary": None,
                "body_md": None,
                "image_url": f"/images/{year_dir}/{date_str}.jpg",
                "source_file": str(src.relative_to(REPO_ROOT)),
                "_src_path": str(src),
            }
        )
    return entries


def compress_image(src_path: Path, dest_path: Path) -> None:
    """Apply EXIF rotation, downscale to MAX_IMAGE_DIM, and re-encode as JPEG.

    These are phone photos of a workout board/log, so JPEG at moderate
    quality is appropriate and shrinks the (originally uncompressed,
    multi-MB) PNGs by roughly 95%. Phones tag rotated shots with an EXIF
    orientation instead of rotating the pixels; ImageOps.exif_transpose()
    applies that so the saved JPEG is upright without the tag (a plain
    .convert("RGB") silently drops the tag and leaves the photo sideways)."""
    with Image.open(src_path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((MAX_IMAGE_DIM, MAX_IMAGE_DIM), Image.LANCZOS)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest_path, "JPEG", quality=JPEG_QUALITY, optimize=True)


def copy_images_for(entries: list[dict]) -> None:
    for entry in entries:
        src_path = entry.pop("_src_path", None)
        if entry["kind"] != "image" or src_path is None:
            continue
        dest = WWW_IMAGES_DIR / Path(entry["image_url"]).relative_to("/images")
        compress_image(Path(src_path), dest)


def dedupe_by_date(entries: list[dict]) -> list[dict]:
    """Some 2020 dates have both a typed text entry and a photographed-log
    image for the same workout. Prefer the text entry (richer content) and
    drop the redundant image so each date appears once."""
    by_date: dict[str, dict] = {}
    for entry in entries:
        existing = by_date.get(entry["date"])
        was_image = existing is not None and existing["kind"] == "image"
        prefer_text = was_image and entry["kind"] == "text"
        if existing is None or prefer_text:
            by_date[entry["date"]] = entry
    return list(by_date.values())


def main() -> None:
    text_entries: list[dict] = []
    for name in RMD_FILES:
        text_entries.extend(parse_rmd(RMD_DIR / name))

    image_entries = collect_image_entries()

    all_entries = dedupe_by_date(text_entries + image_entries)
    all_entries.sort(key=lambda e: e["date"])
    dropped = len(text_entries) + len(image_entries) - len(all_entries)
    copy_images_for(all_entries)

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(all_entries, indent=2) + "\n", encoding="utf-8")

    print(f"text entries:    {len(text_entries)}")
    print(f"image entries:   {len(image_entries)}")
    print(f"dropped (dupes): {dropped}")
    print(f"total:           {len(all_entries)}")
    print(f"written to:      {DATA_PATH}")


if __name__ == "__main__":
    main()
