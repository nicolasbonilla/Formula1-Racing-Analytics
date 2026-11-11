import streamlit as st
import pandas as pd
from utils import f1_fig

# ---------------------------------------------------------
# EXECUTIVE SUMMARY (FILTER-AWARE)
# ---------------------------------------------------------
def render_executive_summary(data):
    st.title("📘 Executive Summary")

    drivers = data["drivers"]
    constructors = data["constructors"]
    races = data["races"]
    results = data["results"]

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    if results.empty:
        st.warning("⚠️ No records match your current filter settings. Please broaden your slider or season selections.")
        return

    # ---------------------------------------------------------
    # KEY METRICS (BASED ON FILTERED RESULTS)
    # ---------------------------------------------------------
    st.subheader("🏎️ Key Metrics Overview")

    total_drivers = results["driver_id"].nunique() if "driver_id" in results.columns else drivers["driver_id"].nunique()
    total_constructors = results["constructor_id"].nunique() if "constructor_id" in results.columns else constructors["constructor_id"].nunique()
    
    if "season" in results.columns and "round" in results.columns:
        total_races = results[["season", "round"]].drop_duplicates().shape[0]
    else:
        total_races = races[["season", "round"]].drop_duplicates().shape[0]

    total_points = results["points"].sum() if "points" in results.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Drivers", total_drivers)
    col2.metric("Constructors", total_constructors)
    col3.metric("Races", total_races)
    col4.metric("Total Points Awarded", int(total_points))

    # ---------------------------------------------------------
    # TOP DRIVER
    # ---------------------------------------------------------
    st.subheader("🏁 Top Driver")

    if "driver_id" in results.columns and not drivers.empty:
        driver_perf = (
            results.groupby("driver_id")["points"]
            .sum()
            .reset_index()
            .merge(
                drivers[["driver_id", "given_name", "family_name"]],
                on="driver_id",
                how="left"
            )
        )
        if "given_name" in driver_perf.columns and "family_name" in driver_perf.columns:
            driver_perf["driver_name"] = driver_perf["given_name"].fillna("") + " " + driver_perf["family_name"].fillna("")
        else:
            driver_perf["driver_name"] = "Driver " + driver_perf["driver_id"].astype(str)
            
        driver_perf = driver_perf.sort_values("points", ascending=False)

        if not driver_perf.empty:
            top_driver = driver_perf.iloc[0]
            st.success(
                f"🏎️ **{top_driver['driver_name'].strip()}** leads with **{top_driver['points']} points**."
            )

    # ---------------------------------------------------------
    # TOP CONSTRUCTOR
    # ---------------------------------------------------------
    st.subheader("🏆 Top Constructor")

    if "constructor_id" in results.columns and not constructors.empty:
        constructor_perf = (
            results.groupby("constructor_id")["points"]
            .sum()
            .reset_index()
            .merge(
                constructors[["constructor_id", "constructor_name"]],
                on="constructor_id",
                how="left"
            )
            .sort_values("points", ascending=False)
        )

        if not constructor_perf.empty:
            top_constructor = constructor_perf.iloc[0]
            c_name = top_constructor.get('constructor_name', 'Constructor')
            st.info(
                f"🏆 **{c_name}** leads constructors with **{top_constructor['points']} points**."
            )

    # ---------------------------------------------------------
    # POINTS DISTRIBUTION ACROSS DRIVERS
    # ---------------------------------------------------------
    st.subheader("📊 Points Distribution Across Drivers")

    if not driver_perf.empty:
        fig = f1_fig("Driver Points Distribution")
        fig.add_bar(
            x=driver_perf["driver_name"].head(15),
            y=driver_perf["points"].head(15),
            marker_color="#ff1e00"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "📌 *This chart highlights the most dominant drivers in the filtered dataset.*"
    )

    st.success("Executive Summary loaded successfully.")