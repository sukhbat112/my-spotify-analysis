"""Print a Wrapped++ summary of your streaming history in the terminal.

 run it with:
    python scripts/make_wrapped.py
    python scripts/make_wrapped.py --year 2024

"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# to print emoji, force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# helper_scripts.py sits next to this file in scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from helper_scripts import clean_streams, load_streams  # noqa: E402


def _print_top(title: str, grouped) -> None:
    print(f"\n{title}")
    for i, (name, minutes) in enumerate(grouped.items(), 1):
        label = " - ".join(name) if isinstance(name, tuple) else name
        print(f"  {i:>2}. {label}  ({int(minutes):,} minutes)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=None, help="restrict to a single year")
    args = ap.parse_args()

    print("Loading + cleaning streams...")
    df = clean_streams(load_streams())
    if args.year:
        df = df[df["year"] == args.year]

    t = df[df["is_track"]]
    minutes = t["minutes"].sum()
    scope = f"YEAR {args.year}" if args.year else "ALL TIME"
    bar = "=" * 52
    print(f"\n{bar}\n  🎧 WRAPPED++   {scope}\n{bar}")
    print(f"  Range:          {df['ts'].min():%Y-%m-%d} to {df['ts'].max():%Y-%m-%d}")
    print(f"  Streams:        {len(t):,}")
    print(f"  Minutes:        {minutes:,.0f}  ({minutes / 60 / 24:.1f} full days)")
    print(f"  Unique artists: {t['artist'].nunique():,}")
    print(f"  Unique tracks:  {t['spotify_track_uri'].nunique():,}")
    print(f"  Skip rate:      {t['skipped'].mean():.1%}")

    top_artists = t.groupby("artist")["minutes"].sum().sort_values(ascending=False).head(10)
    _print_top("🎤 Top artists (by minutes):", top_artists)

    top_tracks = (t.groupby(["artist", "track"])["minutes"].sum()
                  .sort_values(ascending=False).head(10))
    _print_top("🎵 Top tracks (by minutes):", top_tracks)

    print("\n🌍 Where you listened:")
    countries = t.groupby("conn_country")["track"].size().sort_values(ascending=False).head(6)
    for country, n in countries.items():
        print(f"  {country}: {int(n):,} streams")


if __name__ == "__main__":
    main()
