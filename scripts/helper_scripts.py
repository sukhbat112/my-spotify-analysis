"""Load and clean my Spotify Extended Streaming History into one tidy DataFrame.

This is the only shared helper the notebooks import. Everything else (the analysis,
the plots, the models) lives inline in the notebooks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# paths (this file is in scripts/, so parents[1] is the repo root)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"        # your unzipped spotify export (gitignored)
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"  # tiny synthetic sample

# a play counts as a real listen above this (spotify's own threshold).
MIN_LISTEN_MS = 30_000  # 30 seconds

# rename the long metadata fields.
RENAME = {
    "master_metadata_track_name": "track",
    "master_metadata_album_artist_name": "artist",
    "master_metadata_album_album_name": "album",
}

# Booleans arrive from JSON as True/False/None, coerce to pandas nullable boolean.
BOOL_COLS = ["shuffle", "skipped", "offline", "incognito_mode"]


def load_streams(source: Path | str | None = None, *, audio_only: bool = True) -> pd.DataFrame:
    """Read every Streaming_History_Audio_*.json into one DataFrame, sorted by time.

    Looks in data/raw, then a my_spotify_data/ folder, then the bundled sample
     Adds derived columns: minutes, year, date, hour, weekday,is_track, is_podcast.
    """
    pattern = "Streaming_History_Audio_*.json" if audio_only else "Streaming_History_*.json"
    if source is not None:
        search_dirs = [Path(source)]
    else:
        search_dirs = [RAW_DIR, PROJECT_ROOT / "my_spotify_data", SAMPLE_DIR]

    files: list[Path] = []
    for d in search_dirs:
        files = sorted(d.rglob(pattern))
        if files:
            break
    if not files:
        raise FileNotFoundError(
            f"No {pattern!r} files found in {[str(d) for d in search_dirs]}. "
            "Unzip your Spotify export into data/raw/."
        )

    records: list[dict] = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            records.extend(json.load(fh))

    df = pd.DataFrame.from_records(records).rename(columns=RENAME)
    return _add_derived(df)


def _add_derived(df: pd.DataFrame) -> pd.DataFrame:
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.sort_values("ts").reset_index(drop=True)
    df["minutes"] = df["ms_played"] / 60_000
    df["year"] = df["ts"].dt.year
    df["date"] = df["ts"].dt.date
    df["hour"] = df["ts"].dt.hour
    df["weekday"] = df["ts"].dt.day_name()
    df["is_podcast"] = df.get("episode_name").notna() if "episode_name" in df else False
    df["is_track"] = df["track"].notna()
    return df


def clean_streams(df: pd.DataFrame, *, drop_incognito: bool = False) -> pd.DataFrame:
    """Coerce booleans, trim text, drop duplicate logs, flag real listens (>= 30s)."""
    out = df.copy()
    for col in BOOL_COLS:
        if col in out:
            out[col] = out[col].astype("boolean")
    for col in ("track", "artist", "album"):
        if col in out:
            out[col] = out[col].str.strip()

    dedup_keys = [k for k in ("ts", "spotify_track_uri", "ms_played") if k in out]
    out = out.drop_duplicates(subset=dedup_keys).reset_index(drop=True)
    if drop_incognito and "incognito_mode" in out:
        out = out[out["incognito_mode"] != True].reset_index(drop=True)  # noqa: E712

    out["is_real_listen"] = out["ms_played"] >= MIN_LISTEN_MS
    return out
