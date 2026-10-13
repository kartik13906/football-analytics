"""
app.py  –  Football Player Performance Analytics Dashboard
===========================================================
⚠️  All data is SYNTHETIC and generated solely for demonstration purposes.
    Statistics do NOT represent real-world football players or results.

Run:
    streamlit run app.py
"""

import os
import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (dark / football-green theme) ──────────────────────────────────
st.markdown(
    """
<style>
/* ── global ── */
html, body, [data-testid="stApp"] {
    background-color: #0d1117;
    color: #e6edf3;
}
/* ── sidebar ── */
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 2px solid #1a7f37;
}
[data-testid="stSidebar"] .st-emotion-cache-1cypcdb { color: #e6edf3; }
/* ── metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #161b22 0%, #0d2818 100%);
    border: 1px solid #1a7f37;
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"]  { color: #8b949e !important; font-size: 0.85rem; }
[data-testid="stMetricValue"]  { color: #3fb950 !important; font-size: 2rem; font-weight: 700; }
[data-testid="stMetricDelta"]  { color: #58a6ff !important; }
/* ── tabs ── */
[data-testid="stTabs"] button[aria-selected="true"] {
    border-bottom: 3px solid #3fb950;
    color: #3fb950;
}
/* ── headers ── */
h1, h2, h3 { color: #3fb950; }
/* ── dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1a7f37; border-radius: 6px; }
/* ── buttons ── */
[data-testid="stDownloadButton"] button {
    background-color: #1a7f37 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
}
/* ── selectbox / multiselect ── */
[data-testid="stSelectbox"] div,
[data-testid="stMultiSelect"] div { color: #e6edf3; }
/* ── dividers ── */
hr { border-color: #1a7f37; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Plotly theme helper ────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font_color="#e6edf3",
    colorway=["#3fb950", "#58a6ff", "#f78166", "#d2a8ff", "#ffa657", "#79c0ff"],
)

GREEN_SEQ = px.colors.sequential.Greens


def styled_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        **PLOTLY_THEME,
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
        yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    )
    return fig


# ── Data loading ──────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "football_players.csv")

REQUIRED_COLUMNS = {
    "player_id", "player_name", "team", "season", "position",
    "nationality", "age", "appearances", "minutes_played",
    "goals", "assists", "shots", "shots_on_target", "passes",
    "key_passes", "tackles", "interceptions", "saves",
    "yellow_cards", "red_cards", "rating",
}


@st.cache_data(show_spinner="Loading player data …")
def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_FILE):
        st.error(
            f"❌  Data file not found: `{DATA_FILE}`\n\n"
            "Run `python generate_data.py` to create it, then restart the app."
        )
        st.stop()

    df = pd.read_csv(DATA_FILE)

    # ── Validate columns ──
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        st.error(f"❌  Missing columns in CSV: {', '.join(sorted(missing_cols))}")
        st.stop()

    # ── Coerce numeric columns ──
    num_cols = [
        "age", "appearances", "minutes_played", "goals", "assists",
        "shots", "shots_on_target", "passes", "key_passes", "tackles",
        "interceptions", "saves", "yellow_cards", "red_cards", "rating",
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Drop rows with nulls in key fields ──
    key_fields = ["player_name", "team", "position", "season"]
    before = len(df)
    df = df.dropna(subset=key_fields)
    dropped = before - len(df)
    if dropped:
        st.warning(f"⚠️  Dropped {dropped} rows with missing key values.")

    # ── Fill remaining numeric NaN with 0 ──
    df[num_cols] = df[num_cols].fillna(0)

    if len(df) == 0:
        st.error("❌  No valid data rows remain after cleaning.")
        st.stop()

    return df


# ── Sidebar filters ────────────────────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame):
    st.sidebar.title("⚽ Filters")
    st.sidebar.markdown("---")

    seasons = sorted(df["season"].unique())
    sel_seasons = st.sidebar.multiselect(
        "Season", seasons, default=seasons, key="filter_season"
    )

    teams = sorted(df["team"].unique())
    sel_teams = st.sidebar.multiselect(
        "Team", teams, default=teams, key="filter_team"
    )

    positions = sorted(df["position"].unique())
    sel_positions = st.sidebar.multiselect(
        "Position", positions, default=positions, key="filter_position"
    )

    # Apply season / team / position filters first
    mask = (
        df["season"].isin(sel_seasons if sel_seasons else seasons)
        & df["team"].isin(sel_teams if sel_teams else teams)
        & df["position"].isin(sel_positions if sel_positions else positions)
    )
    filtered = df[mask]

    players = sorted(filtered["player_name"].unique())
    sel_players = st.sidebar.multiselect(
        "Player (optional)", players, default=[], key="filter_player"
    )

    if sel_players:
        filtered = filtered[filtered["player_name"].isin(sel_players)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"**{len(filtered)}** of **{len(df)}** players shown")

    return filtered


# ── KPI calculations ──────────────────────────────────────────────────────────
def calc_kpis(df: pd.DataFrame) -> dict:
    return dict(
        total_players=len(df),
        total_goals=int(df["goals"].sum()),
        total_assists=int(df["assists"].sum()),
        total_minutes=int(df["minutes_played"].sum()),
        avg_rating=round(float(df["rating"].mean()), 2) if len(df) else 0.0,
    )


def fmt_large(n: int) -> str:
    """Format large integers with comma separators."""
    return f"{n:,}"


# ── CSV download helper ────────────────────────────────────────────────────────
def csv_download_button(df: pd.DataFrame, label: str = "⬇️  Download filtered data as CSV"):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button(
        label=label,
        data=buf.getvalue().encode("utf-8"),
        file_name="football_players_filtered.csv",
        mime="text/csv",
    )


# ── Page: Overview ────────────────────────────────────────────────────────────
def page_overview(df: pd.DataFrame):
    st.title("⚽ Football Player Performance Analytics")
    st.caption(
        "⚠️  **Synthetic data** — all figures are randomly generated for demonstration only."
    )
    st.markdown("---")

    kpis = calc_kpis(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Players",    fmt_large(kpis["total_players"]))
    c2.metric("⚽ Total Goals",      fmt_large(kpis["total_goals"]))
    c3.metric("🎯 Total Assists",    fmt_large(kpis["total_assists"]))
    c4.metric("⏱️ Minutes Played",  fmt_large(kpis["total_minutes"]))
    c5.metric("⭐ Avg Rating",       f"{kpis['avg_rating']:.2f}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    # Top 10 scorers bar chart
    with col_l:
        st.subheader("🏆 Top 10 Goal Scorers")
        top_scorers = (
            df.groupby("player_name", as_index=False)["goals"]
            .sum()
            .nlargest(10, "goals")
        )
        fig = px.bar(
            top_scorers,
            x="goals",
            y="player_name",
            orientation="h",
            labels={"goals": "Goals", "player_name": ""},
            text="goals",
            color="goals",
            color_continuous_scale=GREEN_SEQ,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    # Goals distribution by position
    with col_r:
        st.subheader("📊 Goals Distribution by Position")
        pos_goals = df.groupby("position", as_index=False)["goals"].sum()
        fig2 = px.pie(
            pos_goals,
            names="position",
            values="goals",
            color_discrete_sequence=PLOTLY_THEME["colorway"],
            hole=0.4,
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    # Rating distribution
    st.subheader("📈 Player Rating Distribution")
    fig3 = px.histogram(
        df,
        x="rating",
        nbins=30,
        color_discrete_sequence=["#3fb950"],
        labels={"rating": "Rating", "count": "Players"},
        opacity=0.85,
    )
    fig3.update_layout(bargap=0.05)
    st.plotly_chart(styled_fig(fig3), use_container_width=True)


# ── Page: Player Analysis ─────────────────────────────────────────────────────
def page_player_analysis(df: pd.DataFrame):
    st.title("🔍 Player Analysis")
    st.markdown("---")

    # ── Player comparison ──
    st.subheader("🆚 Player Comparison")
    all_players = sorted(df["player_name"].unique())

    if len(all_players) < 2:
        st.info("Select at least 2 players in the sidebar to compare.")
        return

    default_two = all_players[:2]
    compare_players = st.multiselect(
        "Select players to compare (2–6)",
        all_players,
        default=default_two,
        key="compare_select",
    )

    if len(compare_players) < 2:
        st.warning("Please select at least 2 players.")
    else:
        cmp_df = (
            df[df["player_name"].isin(compare_players)]
            .groupby("player_name", as_index=False)
            .agg(
                Goals=("goals", "sum"),
                Assists=("assists", "sum"),
                Shots=("shots", "sum"),
                Passes=("passes", "sum"),
                Tackles=("tackles", "sum"),
                Rating=("rating", "mean"),
            )
        )
        cmp_df["Rating"] = cmp_df["Rating"].round(2)

        radar_cats = ["Goals", "Assists", "Shots", "Passes", "Tackles", "Rating"]

        # Normalise to 0-1 for radar
        norm = cmp_df.copy()
        for cat in radar_cats:
            rng = norm[cat].max() - norm[cat].min()
            norm[cat] = (norm[cat] - norm[cat].min()) / rng if rng else 0.5

        radar_fig = go.Figure()
        colors = PLOTLY_THEME["colorway"]
        for i, row in norm.iterrows():
            vals = [row[c] for c in radar_cats] + [row[radar_cats[0]]]
            radar_fig.add_trace(
                go.Scatterpolar(
                    r=vals,
                    theta=radar_cats + [radar_cats[0]],
                    fill="toself",
                    name=row["player_name"],
                    line_color=colors[i % len(colors)],
                    opacity=0.7,
                )
            )
        radar_fig.update_layout(
            polar=dict(
                bgcolor="#0d2818",
                radialaxis=dict(visible=True, range=[0, 1], color="#8b949e"),
                angularaxis=dict(color="#e6edf3"),
            ),
            showlegend=True,
        )
        st.plotly_chart(styled_fig(radar_fig), use_container_width=True)

        st.dataframe(
            cmp_df.set_index("player_name").T,
            use_container_width=True,
        )

    st.markdown("---")

    # ── Goals vs Assists scatter ──
    st.subheader("⚽ Goals vs Assists")
    scatter_df = df.groupby(["player_name", "position", "team"], as_index=False).agg(
        Goals=("goals", "sum"),
        Assists=("assists", "sum"),
        Rating=("rating", "mean"),
        Minutes=("minutes_played", "sum"),
    )
    scatter_df["Rating"] = scatter_df["Rating"].round(2)

    fig_sc = px.scatter(
        scatter_df,
        x="Goals",
        y="Assists",
        color="position",
        size="Minutes",
        hover_name="player_name",
        hover_data={"team": True, "Rating": True, "Minutes": True},
        labels={"position": "Position"},
        color_discrete_sequence=PLOTLY_THEME["colorway"],
        size_max=25,
    )
    fig_sc.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color="#ffffff")))
    st.plotly_chart(styled_fig(fig_sc), use_container_width=True)

    st.markdown("---")

    # ── Shots vs Goals analysis ──
    st.subheader("🎯 Shots vs Goals (Conversion Rate)")
    shots_df = df.groupby(["player_name", "position"], as_index=False).agg(
        Goals=("goals", "sum"),
        Shots=("shots", "sum"),
        SoT=("shots_on_target", "sum"),
    )
    shots_df["Conversion %"] = np.where(
        shots_df["Shots"] > 0,
        (shots_df["Goals"] / shots_df["Shots"] * 100).round(1),
        0.0,
    )

    fig_shots = px.scatter(
        shots_df,
        x="Shots",
        y="Goals",
        color="Conversion %",
        hover_name="player_name",
        hover_data={"position": True, "SoT": True, "Conversion %": True},
        color_continuous_scale=GREEN_SEQ,
        labels={"SoT": "Shots on Target"},
    )
    fig_shots.update_traces(marker=dict(size=9, opacity=0.85))
    st.plotly_chart(styled_fig(fig_shots), use_container_width=True)


# ── Page: Team Analysis ───────────────────────────────────────────────────────
def page_team_analysis(df: pd.DataFrame):
    st.title("🏟️ Team Analysis")
    st.markdown("---")

    team_df = (
        df.groupby("team", as_index=False)
        .agg(
            Goals=("goals", "sum"),
            Assists=("assists", "sum"),
            Players=("player_name", "nunique"),
            Avg_Rating=("rating", "mean"),
            Total_Minutes=("minutes_played", "sum"),
        )
        .sort_values("Goals", ascending=False)
    )
    team_df["Avg_Rating"] = team_df["Avg_Rating"].round(2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚽ Goals per Team")
        fig1 = px.bar(
            team_df,
            x="team",
            y="Goals",
            color="Goals",
            color_continuous_scale=GREEN_SEQ,
            text="Goals",
            labels={"team": "Team"},
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(xaxis_tickangle=-35, coloraxis_showscale=False)
        st.plotly_chart(styled_fig(fig1), use_container_width=True)

    with col2:
        st.subheader("🎯 Assists per Team")
        fig2 = px.bar(
            team_df,
            x="team",
            y="Assists",
            color="Assists",
            color_continuous_scale=px.colors.sequential.Blues,
            text="Assists",
            labels={"team": "Team"},
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(xaxis_tickangle=-35, coloraxis_showscale=False)
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    st.subheader("👥 Squad Size & Average Rating")
    fig3 = px.scatter(
        team_df,
        x="Players",
        y="Avg_Rating",
        size="Goals",
        color="team",
        hover_name="team",
        hover_data={"Goals": True, "Assists": True, "Total_Minutes": True},
        labels={"Avg_Rating": "Avg. Rating", "Players": "Squad Size"},
        color_discrete_sequence=PLOTLY_THEME["colorway"],
        size_max=35,
    )
    fig3.update_traces(marker=dict(opacity=0.85))
    st.plotly_chart(styled_fig(fig3), use_container_width=True)

    st.subheader("📋 Team Summary Table")
    display_cols = {
        "team": "Team",
        "Goals": "Goals",
        "Assists": "Assists",
        "Players": "Players",
        "Avg_Rating": "Avg Rating",
        "Total_Minutes": "Total Minutes",
    }
    st.dataframe(
        team_df.rename(columns=display_cols)[list(display_cols.values())],
        use_container_width=True,
        hide_index=True,
    )


# ── Page: Position Analysis ───────────────────────────────────────────────────
def page_position_analysis(df: pd.DataFrame):
    st.title("📌 Position Analysis")
    st.markdown("---")

    positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
    pos_tabs = st.tabs(positions)

    stat_map = {
        "Goalkeeper": {
            "primary": ("saves", "Saves"),
            "metrics": ["saves", "goals", "assists", "yellow_cards", "red_cards", "rating"],
        },
        "Defender": {
            "primary": ("tackles", "Tackles"),
            "metrics": ["tackles", "interceptions", "goals", "assists", "yellow_cards", "rating"],
        },
        "Midfielder": {
            "primary": ("passes", "Passes"),
            "metrics": ["passes", "key_passes", "goals", "assists", "tackles", "rating"],
        },
        "Forward": {
            "primary": ("goals", "Goals"),
            "metrics": ["goals", "assists", "shots", "shots_on_target", "key_passes", "rating"],
        },
    }

    for tab, pos in zip(pos_tabs, positions):
        with tab:
            pos_df = df[df["position"] == pos]
            if pos_df.empty:
                st.info(f"No data for {pos} with current filters.")
                continue

            cfg = stat_map[pos]
            stat_col, stat_label = cfg["primary"]

            kpis = {
                "count": len(pos_df),
                "avg_rating": pos_df["rating"].mean(),
                "stat_sum": pos_df[stat_col].sum(),
                "stat_mean": pos_df[stat_col].mean(),
            }

            kc1, kc2, kc3, kc4 = st.columns(4)
            kc1.metric("Players", fmt_large(kpis["count"]))
            kc2.metric("Avg Rating", f"{kpis['avg_rating']:.2f}")
            kc3.metric(f"Total {stat_label}", fmt_large(int(kpis["stat_sum"])))
            kc4.metric(f"Avg {stat_label}", f"{kpis['stat_mean']:.1f}")

            st.markdown("---")
            col_a, col_b = st.columns(2)

            # Top players bar
            with col_a:
                st.subheader(f"Top {pos}s by {stat_label}")
                top = (
                    pos_df.groupby("player_name", as_index=False)[stat_col]
                    .sum()
                    .nlargest(10, stat_col)
                )
                fig = px.bar(
                    top,
                    x=stat_col,
                    y="player_name",
                    orientation="h",
                    text=stat_col,
                    color=stat_col,
                    color_continuous_scale=GREEN_SEQ,
                    labels={stat_col: stat_label, "player_name": ""},
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    coloraxis_showscale=False,
                )
                st.plotly_chart(styled_fig(fig), use_container_width=True)

            # Metric distribution box
            with col_b:
                st.subheader(f"Rating Distribution — {pos}s")
                fig2 = px.box(
                    pos_df,
                    x="team",
                    y="rating",
                    color="team",
                    labels={"rating": "Rating", "team": "Team"},
                    color_discrete_sequence=PLOTLY_THEME["colorway"],
                )
                fig2.update_layout(
                    xaxis_tickangle=-35,
                    showlegend=False,
                )
                st.plotly_chart(styled_fig(fig2), use_container_width=True)

            # Multi-stat grouped bar for position-specific metrics
            st.subheader(f"Average Stats Breakdown — {pos}s by Team")
            avg_stats = (
                pos_df.groupby("team")[cfg["metrics"]]
                .mean()
                .reset_index()
            )
            fig3 = px.bar(
                avg_stats.melt(id_vars="team", var_name="Stat", value_name="Average"),
                x="team",
                y="Average",
                color="Stat",
                barmode="group",
                labels={"team": "Team"},
                color_discrete_sequence=PLOTLY_THEME["colorway"],
            )
            fig3.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(styled_fig(fig3), use_container_width=True)


# ── Page: Player Statistics Table ────────────────────────────────────────────
def page_stats_table(df: pd.DataFrame):
    st.title("📋 Player Statistics Table")
    st.markdown("---")

    # Searchable text filter
    search = st.text_input(
        "🔎 Search player or team",
        placeholder="Type a player name or team …",
        key="table_search",
    )

    display_df = df.copy()
    if search.strip():
        mask = (
            display_df["player_name"].str.contains(search, case=False, na=False)
            | display_df["team"].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]

    if display_df.empty:
        st.warning(f'No players found for "{search}".')
        return

    # Rename for display
    rename = {
        "player_id": "ID", "player_name": "Player", "team": "Team",
        "season": "Season", "position": "Position", "nationality": "Nationality",
        "age": "Age", "appearances": "Apps", "minutes_played": "Minutes",
        "goals": "Goals", "assists": "Assists", "shots": "Shots",
        "shots_on_target": "SoT", "passes": "Passes", "key_passes": "Key Passes",
        "tackles": "Tackles", "interceptions": "Interceptions", "saves": "Saves",
        "yellow_cards": "YC", "red_cards": "RC", "rating": "Rating",
    }
    st.dataframe(
        display_df.rename(columns=rename).reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Showing {len(display_df):,} players")
    csv_download_button(display_df)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df_full = load_data()
    df = sidebar_filters(df_full)

    if df.empty:
        st.warning("⚠️  No data matches the current filters. Adjust the sidebar selections.")
        st.stop()

    PAGES = {
        "🏠 Overview": page_overview,
        "🔍 Player Analysis": page_player_analysis,
        "🏟️ Team Analysis": page_team_analysis,
        "📌 Position Analysis": page_position_analysis,
        "📋 Stats Table": page_stats_table,
    }

    st.sidebar.markdown("---")
    st.sidebar.title("📑 Navigation")
    page = st.sidebar.radio("", list(PAGES.keys()), label_visibility="collapsed")

    PAGES[page](df)

    # Global CSV download available on every page
    st.sidebar.markdown("---")
    csv_download_button(df, label="⬇️  Download filtered CSV")


if __name__ == "__main__":
    main()
