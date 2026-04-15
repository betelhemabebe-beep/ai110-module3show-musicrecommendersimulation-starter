"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs

MAX_SCORE = 8.5   # genre(2) + energy(2) + mood(1.5) + valence(1.5) + acoustic(1) + dance(0.5)
DIVIDER   = "-" * 62
HEADER    = "=" * 62


def print_header(user_prefs: dict, k: int) -> None:
    """Print the session header showing the active user profile and max possible score."""
    profile = "  |  ".join(f"{key}={val}" for key, val in user_prefs.items())
    print(f"\n{HEADER}")
    print(f"  Music Recommender  --  Top {k} Results")
    print(HEADER)
    print(f"\n  Profile   : {profile}")
    print(f"  Max score : {MAX_SCORE} pts\n")


def print_result(rank: int, song: dict, score: float, explanation: str) -> None:
    """Print one ranked result with its score, percentage match, and per-feature reasons."""
    pct = round((score / MAX_SCORE) * 100)
    print(DIVIDER)
    print(f"#{rank}  {song['title']}  by {song['artist']}")
    print(f"    Score : {score:.2f} / {MAX_SCORE}  ({pct}% match)")
    print()
    for reason in explanation.split(" | "):
        print(f"    {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {
        "genre":        "pop",
        "mood":         "happy",
        "energy":       0.80,
        "valence":      0.80,
        "acoustic":     False,
        "danceability": 0.80,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print_header(user_prefs, k=5)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_result(rank, song, score, explanation)

    print(HEADER)
    print()


if __name__ == "__main__":
    main()
