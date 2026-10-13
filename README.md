# ⚽ Football Player Performance Analytics Dashboard

> **⚠️ Synthetic Data Notice**  
> All player statistics in `football_players.csv` are entirely randomly generated
> for demonstration purposes. They do **not** represent any real-world football
> players, clubs, or match results.

---

## 📌 Features

| # | Feature |
|---|---------|
| 1 | **Overview page** — KPI cards (total players, goals, assists, minutes, avg rating), top scorers bar, goals-by-position pie, rating histogram |
| 2 | **Player Analysis** — radar-chart player comparison (2–6 players), goals vs assists scatter, shots vs goals conversion scatter |
| 3 | **Team Analysis** — goals/assists bar charts per team, squad-size scatter, summary table |
| 4 | **Position Analysis** — dedicated tab per position (GK / DEF / MID / FWD) with top performers, rating box-plot, avg-stats grouped bar |
| 5 | **Sidebar filters** — season, team, position, player (cascading) |
| 6 | **Searchable stats table** — text search on player name or team |
| 7 | **CSV download** — filtered data, available in Stats Table page and sidebar |
| 8 | **Dark football-green UI** — custom CSS, Plotly dark theme |
| 9 | **Responsive layout** — two-column grids, clear labels and tooltips on all charts |
| 10 | **Input validation** — missing-column check, NaN handling, empty-filter guard, informative error messages |

---

## 🗂️ Project Structure

```
football_analytics/
├── app.py               ← Main Streamlit application
├── generate_data.py     ← Synthetic dataset generator
├── football_players.csv ← Pre-generated dataset (120 players)
├── requirements.txt     ← Python dependencies
└── README.md            ← This file
```

---

## 📊 Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `player_id` | int | Unique row identifier |
| `player_name` | str | First + last name |
| `team` | str | One of 10 synthetic clubs |
| `season` | str | 2021/22, 2022/23, or 2023/24 |
| `position` | str | Goalkeeper / Defender / Midfielder / Forward |
| `nationality` | str | One of 10 nationalities |
| `age` | int | 17–36 |
| `appearances` | int | 5–37 |
| `minutes_played` | int | appearances × random 45–94 |
| `goals` | int | Position-weighted distribution |
| `assists` | int | Position-weighted distribution |
| `shots` | int | Position-weighted distribution |
| `shots_on_target` | int | ≤ shots |
| `passes` | int | Position-weighted distribution |
| `key_passes` | int | Position-weighted distribution |
| `tackles` | int | Position-weighted distribution |
| `interceptions` | int | Position-weighted distribution |
| `saves` | int | High for GKs, near zero for others |
| `yellow_cards` | int | 0–10 |
| `red_cards` | int | 0–2 |
| `rating` | float | 6.0–9.8 (position-weighted) |

---

## 🧮 KPI Calculations

All KPIs are computed from the **currently filtered** DataFrame at runtime:

| KPI | Calculation |
|-----|-------------|
| Total Players | `len(df)` |
| Total Goals | `df["goals"].sum()` |
| Total Assists | `df["assists"].sum()` |
| Total Minutes | `df["minutes_played"].sum()` |
| Avg Rating | `df["rating"].mean()` |

---

## 🚀 Running Locally

### Prerequisites

- Python 3.10+
- A virtual environment (recommended)

### 1 — Clone / download the project

```bash
git clone <your-repo-url>
cd football_analytics
```

### 2 — Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3 — Generate the dataset (if `football_players.csv` is missing)

```bash
python generate_data.py
```

### 4 — Launch the dashboard

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push this folder to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **New app** → select your repo, branch, and set the main file to `app.py`.
4. Click **Deploy** — Streamlit Cloud reads `requirements.txt` automatically.

> Make sure `football_players.csv` is committed to the repo, **or** add a
> `@st.cache_data` call in `app.py` that regenerates it on startup (already
> handled: the app stops with a clear error if the CSV is missing and tells you
> to run `generate_data.py`).

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| [Streamlit](https://streamlit.io) | Dashboard framework |
| [Pandas](https://pandas.pydata.org) | Data manipulation |
| [NumPy](https://numpy.org) | Numerical generation / vectorised ops |
| [Plotly Express](https://plotly.com/python/plotly-express/) | High-level charts |
| [Plotly Graph Objects](https://plotly.com/python/graph-objects/) | Radar chart |
