
import streamlit as st
from theme import set_theme
from utils import load_table
import pandas as pd
# Section imports
from sections.executive_summary import render_executive_summary
from sections.rq1_driver_constructor import render_rq1
from sections.rq2_race_outcomes import render_rq2
from sections.rq3_circuit_geography import render_rq3
from sections.rq4_sprint_race import render_rq4
from sections.rq5_cross_dataset import render_rq5

from sections import rq6_graphic_llm_rag

# ---------------------------------------------------------
# 1. PAGE CONFIG + THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="F1 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide"
)

set_theme()

# ---------------------------------------------------------
# 2. LOAD ALL REQUIRED DATASETS (Gold + Silver)
# ---------------------------------------------------------
@st.cache_data
def load_all_data():
    return {
        "drivers": load_table("drivers"),
        "constructors": load_table("constructors"),
        "races": load_table("races"),
        "results": load_table("results"),
        "circuits": load_table("circuits"),
        "sprints": load_table("sprints"),
    }

data = load_all_data()

# [Rest of your app.py remains the same...]

# ---------------------------------------------------------
# 3. GLOBAL FILTERS (ONLY SEASON + SLIDERS)
# ---------------------------------------------------------
st.sidebar.title("🔍 Filters")

drivers = data["drivers"]
constructors = data["constructors"]
races = data["races"]
results = data["results"]

# Ensure GOLD schema is correct
if "season" not in races.columns:
    st.error("❌ Races table missing 'season' column — check Gold layer.")
    st.stop()

# Remove 2026 from options
season_list = sorted([s for s in races["season"].dropna().unique() if s != 2027])

# Default seasons
default_seasons = [s for s in [2024, 2025, 2026] if s in season_list]

seasons = st.sidebar.multiselect(
    "Season",
    season_list,
    default=default_seasons
)

# Sliders
grid_min, grid_max = st.sidebar.slider("Grid Position", 1, 20, (1, 20))
final_min, final_max = st.sidebar.slider("Final Position", 1, 20, (1, 20))
points_min, points_max = st.sidebar.slider("Points", 0, 30, (0, 30))

# ---------------------------------------------------------
# 4. APPLY FILTERS
# ---------------------------------------------------------
filtered_results = results.copy()

# Apply numeric position and points sliders directly on results
filtered_results = filtered_results[
    (filtered_results["grid_position"].between(grid_min, grid_max)) &
    (filtered_results["final_position"].between(final_min, final_max)) &
    (filtered_results["points"].between(points_min, points_max))
]

# ---------------------------------------------------------
# 5. SIDEBAR NAVIGATION
# ---------------------------------------------------------
page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Summary",
        "RQ1 — Driver & Constructor Insights",
        "RQ2 — Race Outcome Analytics",
        "RQ3 — Circuit Geography",
        "RQ4 — Sprint Race Analysis",
        "RQ5 — Cross‑Dataset Insights",
        "RQ6: Graphic-LLM-RAG & ML Engine"
    ]
)

# ---------------------------------------------------------
# 6. ROUTE TO SELECTED PAGE
# ---------------------------------------------------------
filtered_data = {
    **data,
    "results": filtered_results
}

if page == "Executive Summary":
    render_executive_summary(filtered_data)

elif page == "RQ1 — Driver & Constructor Insights":
    render_rq1(filtered_data["results"])

elif page == "RQ2 — Race Outcome Analytics":
    render_rq2(filtered_data)

elif page == "RQ3 — Circuit Geography":
    try:
        res_df = filtered_data["results"]
        races_df = data["races"]
        circuits_df = data["circuits"]
        
        # Merge results with races to attach 'season' and 'circuit_id'
        rq3_df = res_df.merge(races_df, on="race_id" if "race_id" in res_df.columns else ["season", "round"], how="inner")
        
        # Merge with circuits to get country details
        if "circuit_id" in rq3_df.columns and "circuit_id" in circuits_df.columns:
            rq3_df = rq3_df.merge(circuits_df, on="circuit_id", how="left")
            
        # Standardize country column name
        if "country" in rq3_df.columns and "circuit_country" not in rq3_df.columns:
            rq3_df["circuit_country"] = rq3_df["country"]
        elif "location_country" in rq3_df.columns and "circuit_country" not in rq3_df.columns:
            rq3_df["circuit_country"] = rq3_df["location_country"]

        # Apply season filter AFTER the merge if seasons are selected
        if len(seasons) > 0 and "season" in rq3_df.columns:
            rq3_df = rq3_df[rq3_df["season"].isin(seasons)]

        render_rq3(rq3_df)
    except Exception as e:
        st.error(f"Error loading RQ3 Circuit Geography data: {e}")

elif page == "RQ4 — Sprint Race Analysis":
    render_rq4(filtered_data["results"])

elif page == "RQ5 — Cross‑Dataset Insights":
    render_rq5(filtered_data)

elif page == "RQ6: Graphic-LLM-RAG & ML Engine":
    rq6_graphic_llm_rag.render()
# ---------------------------------------------------------
# 7. FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### Built by SRH F1 Student Group — F1 Analytics Platform 🚀")
