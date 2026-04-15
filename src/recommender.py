import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

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
    # New fields with defaults so existing tests keep passing
    popularity: float = 0.0
    release_decade: str = "2020s"
    mood_tags: str = ""
    tempo_feel: str = "medium"
    liveness: float = 0.0

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


# ---------------------------------------------------------------------------
# Scoring mode weight tables
# Each mode redistributes the max 9.5 pts across features differently.
# Keys match the feature names used in score_song().
# ---------------------------------------------------------------------------
SCORING_MODES = {
    "balanced": {
        "genre":         1.0,
        "energy":        4.0,
        "mood":          1.5,
        "valence":       1.5,
        "acoustic":      1.0,
        "danceability":  0.5,
        "popularity":    0.0,
        "liveness":      0.0,
    },
    "genre-first": {
        "genre":         3.0,
        "energy":        2.0,
        "mood":          2.0,
        "valence":       1.0,
        "acoustic":      1.0,
        "danceability":  0.5,
        "popularity":    0.0,
        "liveness":      0.0,
    },
    "mood-first": {
        "genre":         1.0,
        "energy":        2.0,
        "mood":          3.0,
        "valence":       2.0,
        "acoustic":      1.0,
        "danceability":  0.5,
        "popularity":    0.0,
        "liveness":      0.0,
    },
    "energy-focused": {
        "genre":         0.5,
        "energy":        5.5,
        "mood":          1.0,
        "valence":       1.0,
        "acoustic":      1.0,
        "danceability":  0.5,
        "popularity":    0.0,
        "liveness":      0.0,
    },
}


def max_score_for_mode(user_prefs: Dict, mode: str = "balanced") -> float:
    """Return the maximum achievable score given which keys are present in user_prefs."""
    w = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    total = 0.0
    if user_prefs.get("genre"):
        total += w["genre"]
    if "energy" in user_prefs:
        total += w["energy"]
    if user_prefs.get("mood"):
        total += w["mood"]
    if "valence" in user_prefs:
        total += w["valence"]
    if "acoustic" in user_prefs:
        total += w["acoustic"]
    if "danceability" in user_prefs:
        total += w["danceability"]
    if "popularity" in user_prefs:
        total += w["popularity"]
    if "liveness" in user_prefs:
        total += w["liveness"]
    return round(total, 2)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of song dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = {
                "id":             int(row["id"]),
                "title":          row["title"],
                "artist":         row["artist"],
                "genre":          row["genre"],
                "mood":           row["mood"],
                "energy":         float(row["energy"]),
                "tempo_bpm":      float(row["tempo_bpm"]),
                "valence":        float(row["valence"]),
                "danceability":   float(row["danceability"]),
                "acousticness":   float(row["acousticness"]),
                "popularity":     float(row.get("popularity", 0)),
                "release_decade": row.get("release_decade", "2020s"),
                "mood_tags":      row.get("mood_tags", ""),
                "tempo_feel":     row.get("tempo_feel", "medium"),
                "liveness":       float(row.get("liveness", 0)),
            }
            songs.append(song)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, List[str]]:
    """Return (total_score, reasons) comparing song to user_prefs using the given scoring mode."""
    w = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    score = 0.0
    reasons = []

    # --- Genre: categorical, exact match ---
    if user_prefs.get("genre"):
        gw = w["genre"]
        if song["genre"] == user_prefs["genre"]:
            score += gw
            reasons.append(f"genre match: {song['genre']} (+{gw})")
        else:
            reasons.append(f"no genre match: {song['genre']} vs {user_prefs['genre']} (+0.0)")

    # --- Energy: proximity to user target ---
    if "energy" in user_prefs:
        ew = w["energy"]
        pts = round(ew * (1 - abs(user_prefs["energy"] - song["energy"])), 2)
        score += pts
        reasons.append(f"energy {song['energy']} vs target {user_prefs['energy']} (+{pts})")

    # --- Mood: categorical, exact match ---
    if user_prefs.get("mood"):
        mw = w["mood"]
        if song["mood"] == user_prefs["mood"]:
            score += mw
            reasons.append(f"mood match: {song['mood']} (+{mw})")
        else:
            reasons.append(f"no mood match: {song['mood']} vs {user_prefs['mood']} (+0.0)")

    # --- Valence: proximity to user target ---
    if "valence" in user_prefs:
        vw = w["valence"]
        pts = round(vw * (1 - abs(user_prefs["valence"] - song["valence"])), 2)
        score += pts
        reasons.append(f"valence {song['valence']} vs target {user_prefs['valence']} (+{pts})")

    # --- Acousticness: rule-based on likes_acoustic flag ---
    if "acoustic" in user_prefs:
        aw = w["acoustic"]
        if user_prefs["acoustic"]:
            pts = round(aw * song["acousticness"], 2)
        else:
            pts = round(aw * (1 - song["acousticness"]), 2)
        score += pts
        reasons.append(f"acousticness {song['acousticness']} (likes_acoustic={user_prefs['acoustic']}) (+{pts})")

    # --- Danceability: proximity to user target ---
    if "danceability" in user_prefs:
        dw = w["danceability"]
        pts = round(dw * (1 - abs(user_prefs["danceability"] - song["danceability"])), 2)
        score += pts
        reasons.append(f"danceability {song['danceability']} vs target {user_prefs['danceability']} (+{pts})")

    # --- Popularity: proximity to user target (0–100 normalized) ---
    if "popularity" in user_prefs and w["popularity"] > 0:
        pw = w["popularity"]
        pts = round(pw * (1 - abs(user_prefs["popularity"] - song["popularity"]) / 100), 2)
        score += pts
        reasons.append(f"popularity {song['popularity']} vs target {user_prefs['popularity']} (+{pts})")

    # --- Liveness: proximity to user target ---
    if "liveness" in user_prefs and w["liveness"] > 0:
        lw = w["liveness"]
        pts = round(lw * (1 - abs(user_prefs["liveness"] - song["liveness"])), 2)
        score += pts
        reasons.append(f"liveness {song['liveness']} vs target {user_prefs['liveness']} (+{pts})")

    # --- Mood tags: bonus if any user mood_tags word appears in song's mood_tags ---
    if user_prefs.get("mood_tags") and song.get("mood_tags"):
        user_tags = set(user_prefs["mood_tags"].split(";"))
        song_tags = set(song["mood_tags"].split(";"))
        overlap = user_tags & song_tags
        if overlap:
            pts = round(0.1 * len(overlap), 2)
            score += pts
            reasons.append(f"mood tag overlap: {','.join(overlap)} (+{pts})")

    return round(score, 2), reasons


def apply_diversity(scored: List[Tuple[Dict, float, str]],
                    k: int,
                    max_per_artist: int = 1,
                    max_per_genre: int = 2) -> List[Tuple[Dict, float, str]]:
    """
    Greedily select top-k results while limiting same-artist and same-genre repeats.
    Remaining slots are filled from the overflow if needed.
    """
    selected = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    overflow = []

    for item in scored:
        song, score, explanation = item
        a = song["artist"]
        g = song["genre"]
        if (artist_counts.get(a, 0) < max_per_artist and
                genre_counts.get(g, 0) < max_per_genre):
            selected.append(item)
            artist_counts[a] = artist_counts.get(a, 0) + 1
            genre_counts[g] = genre_counts.get(g, 0) + 1
            if len(selected) == k:
                break
        else:
            overflow.append(item)

    # fill remaining slots if diversity was too strict
    while len(selected) < k and overflow:
        selected.append(overflow.pop(0))

    return selected


def recommend_songs(user_prefs: Dict,
                    songs: List[Dict],
                    k: int = 5,
                    mode: str = "balanced",
                    diverse: bool = True) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, apply optional diversity filter, return top k."""
    scored = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song, mode=mode)]
    ]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    if diverse:
        return apply_diversity(ranked, k)
    return ranked[:k]


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top-k Song objects scored against the user profile."""
        prefs = {
            "genre":    user.favorite_genre,
            "mood":     user.favorite_mood,
            "energy":   user.target_energy,
            "acoustic": user.likes_acoustic,
        }
        song_dicts = [
            {
                "id": s.id, "title": s.title, "artist": s.artist,
                "genre": s.genre, "mood": s.mood, "energy": s.energy,
                "tempo_bpm": s.tempo_bpm, "valence": s.valence,
                "danceability": s.danceability, "acousticness": s.acousticness,
                "popularity": s.popularity, "release_decade": s.release_decade,
                "mood_tags": s.mood_tags, "tempo_feel": s.tempo_feel,
                "liveness": s.liveness,
            }
            for s in self.songs
        ]
        results = recommend_songs(prefs, song_dicts, k=k, diverse=False)
        id_to_song = {s.id: s for s in self.songs}
        return [id_to_song[r[0]["id"]] for r in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-text explanation of why this song was recommended."""
        prefs = {
            "genre":    user.favorite_genre,
            "mood":     user.favorite_mood,
            "energy":   user.target_energy,
            "acoustic": user.likes_acoustic,
        }
        song_dict = {
            "id": song.id, "title": song.title, "artist": song.artist,
            "genre": song.genre, "mood": song.mood, "energy": song.energy,
            "tempo_bpm": song.tempo_bpm, "valence": song.valence,
            "danceability": song.danceability, "acousticness": song.acousticness,
            "popularity": song.popularity, "release_decade": song.release_decade,
            "mood_tags": song.mood_tags, "tempo_feel": song.tempo_feel,
            "liveness": song.liveness,
        }
        _, reasons = score_song(prefs, song_dict)
        return " | ".join(reasons)
