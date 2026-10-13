# Football Player Performance Analytics Dashboard — Implementation Plan

## 1. Project Structure

```
football_analytics/
├── app.py               ← Multi-page Streamlit application
├── generate_data.py     ← Reproducible synthetic dataset generator
├── football_players.csv ← Pre-generated CSV (120 rows)
├── requirements.txt     ← streamlit, pandas, numpy, plotly
├── README.md            ← Setup + deploy instructions
└── football-analytics-plan.md  ← This file
```

---

## 2. Dataset Schema

120 synthetic players across 10 teams, 3 seasons, 4 positions.

| Column | Type | Notes |
|--------|------|-------|
| player_id | int | Unique row ID |
| player_name | str | Randomised first + last name (no duplicates) |
| team | str | 10 clubs |
| season | str | 2021/22 · 2022/23 · 2023/24 |
| position | str | GK 10% · DEF 30% · MID 35% · FWD 25% |
| nationality | str | 10 nationalities |
| age | int | 17–36 |
| appearances | int | 5–37 |
| minutes_played | int | appearances × 45–94 |
| goals | int | Position-weighted (FWD highest) |
| assists | int | Position-weighted |
| shots | int | Position-weighted |
| shots_on_target | int | ≤ shots |
| passes | int | Position-weighted (MID highest) |
| key_passes | int | Position-weighted |
| tackles | int | Position-weighted (DEF highest) |
| interceptions | int | Position-weighted |
| saves | int | High for GK; near-zero for others |
| yellow_cards | int | 0–10 |
| red_cards | int | 0–2 |
| rating | float | 6.0–9.8, position-weighted |

Seed: `numpy.random.default_rng(42)` → fully reproducible.

---

## 3. KPI Calculations (computed at runtime, never hardcoded)

| KPI | Formula |
|-----|---------|
| Total Players | `len(df)` |
| Total Goals | `df["goals"].sum()` |
| Total Assists | `df["assists"].sum()` |
| Total Minutes | `df["minutes_played"].sum()` |
| Avg Rating | `df["rating"].mean()` |

All KPIs re-compute whenever sidebar filters change.

---

## 4. Page & Chart Inventory

### Page 1 — Overview
- 5 KPI metric cards (top row)
- Horizontal bar: Top 10 goal scorers
- Donut pie: Goals share by position
- Histogram: Player rating distribution

### Page 2 — Player Analysis
- Radar chart: Up to 6 players compared on 6 normalised stats
- Scatter: Goals vs Assists (colour = position, size = minutes)
- Scatter: Shots vs Goals (colour = conversion %)

### Page 3 — Team Analysis
- Bar: Goals per team
- Bar: Assists per team
- Scatter: Squad size vs avg rating (size = goals)
- Sortable summary table

### Page 4 — Position Analysis
- Tabs: Goalkeeper / Defender / Midfielder / Forward
- Per-tab: 4 KPI cards, top-10 bar, rating box-plot by team, avg-stats grouped bar

### Page 5 — Stats Table
- Full searchable player table (text input filters player_name + team)
- CSV download button for filtered data

---

## 5. Sidebar Filters (cascading)

1. Season (multiselect, all default)
2. Team (multiselect, all default)
3. Position (multiselect, all default)
4. Player (multiselect, optional — populated from filtered set)

---

## 6. UI / Theme

- Dark background `#0d1117` (GitHub-dark style)
- Accent green `#3fb950` / `#1a7f37`
- Custom CSS injected via `st.markdown(..., unsafe_allow_html=True)`
- All Plotly figures use a shared `styled_fig()` helper with matching colours

---

## 7. Input Validation & Error Handling

| Scenario | Handling |
|----------|----------|
| CSV file missing | `st.error` + `st.stop()` |
| Missing columns | `st.error` listing the absent columns + `st.stop()` |
| Non-numeric values | `pd.to_numeric(..., errors="coerce")` → NaN → filled with 0 |
| Null key fields | `dropna(subset=[...])` with `st.warning` showing count |
| Empty filtered result | `st.warning` + `st.stop()` |
| <2 players in comparison | `st.warning` prompt |

---

## 8. Dependencies (requirements.txt)

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.20.0
```

No external APIs, no live data, no optional heavy libraries.
