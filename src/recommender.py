import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of song dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return (total_score, reasons) by comparing song attributes to user_prefs (max 8.5 pts)."""
    score = 0.0
    reasons = []

    # --- Genre: categorical, exact match only ---
    if user_prefs.get("genre"):
        if song["genre"] == user_prefs["genre"]:
            score += 2.0
            reasons.append(f"genre match: {song['genre']} (+2.0)")
        else:
            reasons.append(f"no genre match: {song['genre']} vs {user_prefs['genre']} (+0.0)")

    # --- Energy: proximity to user target (max +2.0) ---
    if "energy" in user_prefs:
        pts = round(2.0 * (1 - abs(user_prefs["energy"] - song["energy"])), 2)
        score += pts
        reasons.append(f"energy {song['energy']} vs target {user_prefs['energy']} (+{pts})")

    # --- Mood: categorical, exact match only ---
    if user_prefs.get("mood"):
        if song["mood"] == user_prefs["mood"]:
            score += 1.5
            reasons.append(f"mood match: {song['mood']} (+1.5)")
        else:
            reasons.append(f"no mood match: {song['mood']} vs {user_prefs['mood']} (+0.0)")

    # --- Valence: proximity to user target (max +1.5) ---
    if "valence" in user_prefs:
        pts = round(1.5 * (1 - abs(user_prefs["valence"] - song["valence"])), 2)
        score += pts
        reasons.append(f"valence {song['valence']} vs target {user_prefs['valence']} (+{pts})")

    # --- Acousticness: rule-based on likes_acoustic flag (max +1.0) ---
    if "acoustic" in user_prefs:
        if user_prefs["acoustic"]:
            pts = round(1.0 * song["acousticness"], 2)
        else:
            pts = round(1.0 * (1 - song["acousticness"]), 2)
        score += pts
        reasons.append(f"acousticness {song['acousticness']} (likes_acoustic={user_prefs['acoustic']}) (+{pts})")

    # --- Danceability: proximity to user target (max +0.5) ---
    if "danceability" in user_prefs:
        pts = round(0.5 * (1 - abs(user_prefs["danceability"] - song["danceability"])), 2)
        score += pts
        reasons.append(f"danceability {song['danceability']} vs target {user_prefs['danceability']} (+{pts})")

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, and return the top k as (song, score, explanation) tuples."""
    scored = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    return ranked[:k]
