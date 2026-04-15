"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs, max_score_for_mode

HEADER  = "=" * 72
DIVIDER = "-" * 72

# ---------------------------------------------------------------------------
# Profiles — each entry: (label, user_prefs, mode)
# mode options: "balanced" | "genre-first" | "mood-first" | "energy-focused"
# ---------------------------------------------------------------------------
PROFILES = [
    (
        "High-Energy Pop",
        {
            "genre":        "pop",
            "mood":         "happy",
            "energy":       0.90,
            "valence":      0.85,
            "acoustic":     False,
            "danceability": 0.88,
        },
        "genre-first",
    ),
    (
        "Chill Lofi",
        {
            "genre":        "lofi",
            "mood":         "chill",
            "energy":       0.38,
            "valence":      0.57,
            "acoustic":     True,
            "danceability": 0.60,
        },
        "mood-first",
    ),
    (
        "Deep Intense Rock",
        {
            "genre":        "rock",
            "mood":         "intense",
            "energy":       0.91,
            "valence":      0.45,
            "acoustic":     False,
            "danceability": 0.65,
        },
        "energy-focused",
    ),
    (
        "Ghost Genre (blues — not in catalog)",
        {
            "genre":        "blues",
            "mood":         "sad",
            "energy":       0.45,
            "valence":      0.30,
            "acoustic":     True,
            "danceability": 0.50,
        },
        "balanced",
    ),
    (
        "Acoustic Paradox (metal + likes_acoustic=True)",
        {
            "genre":        "metal",
            "mood":         "aggressive",
            "energy":       0.95,
            "valence":      0.20,
            "acoustic":     True,
            "danceability": 0.55,
        },
        "energy-focused",
    ),
    (
        "Contradictory Attributes (acoustic=True + energy=0.95)",
        {
            "genre":        "rock",
            "mood":         "intense",
            "energy":       0.95,
            "valence":      0.50,
            "acoustic":     True,
            "danceability": 0.65,
        },
        "genre-first",
    ),
]


def print_table(label: str, user_prefs: dict, mode: str, results: list) -> None:
    """Print recommendations as a clean ASCII summary table."""
    max_pts = max_score_for_mode(user_prefs, mode)

    print(f"\n{HEADER}")
    print(f"  {label}")
    print(f"  Mode: {mode.upper()}  |  Max score: {max_pts} pts")
    print(HEADER)

    # Profile line
    profile_str = "  ".join(f"{k}={v}" for k, v in user_prefs.items())
    print(f"  Profile : {profile_str}")
    print()

    # Column widths
    col_rank   = 4
    col_title  = 24
    col_artist = 18
    col_score  = 14
    col_match  = 7

    # Header row
    header_row = (
        f"  {'#':<{col_rank}}"
        f"{'Title':<{col_title}}"
        f"{'Artist':<{col_artist}}"
        f"{'Score':<{col_score}}"
        f"{'Match':>{col_match}}"
    )
    print(header_row)
    print("  " + "-" * (col_rank + col_title + col_artist + col_score + col_match))

    for rank, (song, score, explanation) in enumerate(results, start=1):
        pct = round((score / max_pts) * 100) if max_pts > 0 else 0
        score_str = f"{score:.2f} / {max_pts}"
        title_trunc  = song["title"][:col_title - 1]
        artist_trunc = song["artist"][:col_artist - 1]
        row = (
            f"  {rank:<{col_rank}}"
            f"{title_trunc:<{col_title}}"
            f"{artist_trunc:<{col_artist}}"
            f"{score_str:<{col_score}}"
            f"{pct:>{col_match - 1}}%"
        )
        print(row)

        # Per-feature breakdown, indented
        for reason in explanation.split(" | "):
            print(f"      {reason}")
        print()

    print(HEADER)
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for label, user_prefs, mode in PROFILES:
        results = recommend_songs(user_prefs, songs, k=3, mode=mode, diverse=True)
        print_table(label, user_prefs, mode, results)


if __name__ == "__main__":
    main()
