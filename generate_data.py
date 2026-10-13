"""
generate_data.py
----------------
Generates a reproducible SYNTHETIC football player dataset and saves it
to football_players.csv.

⚠️  All statistics are entirely fabricated for demonstration purposes.
    They do NOT represent any real-world football players or results.
"""

import numpy as np
import pandas as pd

# ── Reproducibility ──────────────────────────────────────────────────────────
RNG = np.random.default_rng(42)

# ── Lookup tables ─────────────────────────────────────────────────────────────
TEAMS = [
    "FC Northgate", "Southfield United", "Eastbridge City",
    "Westholm Athletic", "Riverton FC", "Crestview Rangers",
    "Lakeside Wanderers", "Hillport Town", "Bayside Rovers", "Pinewood Stars",
]

SEASONS = ["2021/22", "2022/23", "2023/24"]

POSITIONS = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
NATIONALITIES = [
    "English", "Spanish", "French", "Brazilian", "German",
    "Italian", "Portuguese", "Argentine", "Dutch", "Belgian",
]

FIRST_NAMES = [
    "Liam", "Noah", "Oliver", "James", "William", "Benjamin", "Lucas", "Henry",
    "Alexander", "Mason", "Ethan", "Daniel", "Matthew", "Aiden", "Jackson",
    "Sebastian", "Jack", "Owen", "Samuel", "Ryan", "David", "John", "Leo",
    "Gabriel", "Anthony", "Isaiah", "Carter", "Dylan", "Nathan", "Elijah",
    "Marcus", "Victor", "Carlos", "Felix", "Hugo", "Ivan", "Jordan", "Kyle",
    "Leon", "Mario", "Niko", "Oscar", "Paulo", "Remy", "Stefan", "Tomas",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Martinez", "Wilson", "Taylor", "Anderson", "Thomas", "Jackson",
    "White", "Harris", "Martin", "Thompson", "Young", "Allen", "King", "Scott",
    "Perez", "Rivera", "Rossi", "Müller", "Silva", "Santos", "Costa", "Sousa",
    "Fernandez", "Lopez", "Gomez", "Diaz", "Torres", "Reyes", "Morales",
    "Nguyen", "Chen", "Park", "Kim", "Lee", "Zhang", "Liu", "Wang",
]


def _pos_stats(position: str, n: int) -> dict:
    """Return position-appropriate stat distributions."""
    if position == "Goalkeeper":
        return dict(
            goals=RNG.integers(0, 2, n),
            assists=RNG.integers(0, 3, n),
            shots=RNG.integers(0, 5, n),
            shots_on_target=RNG.integers(0, 3, n),
            passes=RNG.integers(20, 45, n),
            key_passes=RNG.integers(0, 3, n),
            tackles=RNG.integers(0, 5, n),
            interceptions=RNG.integers(0, 5, n),
            saves=RNG.integers(20, 90, n),
            yellow_cards=RNG.integers(0, 3, n),
            red_cards=RNG.integers(0, 1, n),
            rating=RNG.uniform(6.0, 8.5, n).round(2),
        )
    if position == "Defender":
        return dict(
            goals=RNG.integers(0, 8, n),
            assists=RNG.integers(0, 10, n),
            shots=RNG.integers(5, 30, n),
            shots_on_target=RNG.integers(2, 15, n),
            passes=RNG.integers(30, 80, n),
            key_passes=RNG.integers(0, 10, n),
            tackles=RNG.integers(20, 80, n),
            interceptions=RNG.integers(15, 70, n),
            saves=RNG.integers(0, 2, n),
            yellow_cards=RNG.integers(0, 8, n),
            red_cards=RNG.integers(0, 2, n),
            rating=RNG.uniform(6.0, 9.0, n).round(2),
        )
    if position == "Midfielder":
        return dict(
            goals=RNG.integers(2, 20, n),
            assists=RNG.integers(3, 20, n),
            shots=RNG.integers(15, 60, n),
            shots_on_target=RNG.integers(5, 30, n),
            passes=RNG.integers(40, 100, n),
            key_passes=RNG.integers(5, 30, n),
            tackles=RNG.integers(10, 60, n),
            interceptions=RNG.integers(5, 40, n),
            saves=RNG.integers(0, 1, n),
            yellow_cards=RNG.integers(0, 10, n),
            red_cards=RNG.integers(0, 2, n),
            rating=RNG.uniform(6.5, 9.5, n).round(2),
        )
    # Forward
    return dict(
        goals=RNG.integers(5, 35, n),
        assists=RNG.integers(2, 20, n),
        shots=RNG.integers(30, 100, n),
        shots_on_target=RNG.integers(10, 55, n),
        passes=RNG.integers(15, 60, n),
        key_passes=RNG.integers(2, 20, n),
        tackles=RNG.integers(2, 25, n),
        interceptions=RNG.integers(1, 15, n),
        saves=RNG.integers(0, 1, n),
        yellow_cards=RNG.integers(0, 8, n),
        red_cards=RNG.integers(0, 2, n),
        rating=RNG.uniform(6.5, 9.8, n).round(2),
    )


def generate(n_players: int = 120) -> pd.DataFrame:
    rows = []
    used_names: set = set()

    for _ in range(n_players):
        while True:
            fn = RNG.choice(FIRST_NAMES)
            ln = RNG.choice(LAST_NAMES)
            name = f"{fn} {ln}"
            if name not in used_names:
                used_names.add(name)
                break

        position = RNG.choice(POSITIONS, p=[0.10, 0.30, 0.35, 0.25])
        team = RNG.choice(TEAMS)
        season = RNG.choice(SEASONS)
        age = int(RNG.integers(17, 37))
        nationality = RNG.choice(NATIONALITIES)
        appearances = int(RNG.integers(5, 38))
        minutes = appearances * int(RNG.integers(45, 95))
        stats = {k: int(v[0]) for k, v in _pos_stats(position, 1).items()}
        # ensure shots_on_target ≤ shots
        stats["shots_on_target"] = min(stats["shots_on_target"], stats["shots"])

        rows.append({
            "player_name": name,
            "team": team,
            "season": season,
            "position": position,
            "nationality": nationality,
            "age": age,
            "appearances": appearances,
            "minutes_played": minutes,
            **stats,
        })

    df = pd.DataFrame(rows)
    df.insert(0, "player_id", range(1, len(df) + 1))
    return df


if __name__ == "__main__":
    df = generate()
    out = "football_players.csv"
    df.to_csv(out, index=False)
    print(f"✅  Saved {len(df)} synthetic players to {out}")
    print(df.dtypes)
    print(df.head(3))
