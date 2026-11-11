import streamlit as st
import plotly.express as px
import pandas as pd

def render_rq1(df):
    st.title("🏎️ RQ1 — Driver & Constructor Performance")

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    if df.empty:
        st.warning("⚠️ No records match your current filter settings. Please broaden your slider or season selections.")
        return

    # Ensure driver_name / constructor_name exist
    if "driver_name" not in df.columns:
        if "family_name" in df.columns:
            df["driver_name"] = df.get("given_name", "") + " " + df["family_name"]
        else:
            df["driver_name"] = "Driver " + df.get("driver_id", pd.Series([1]*len(df))).astype(str)

    if "constructor_name" not in df.columns:
        df["constructor_name"] = "Constructor " + df.get("constructor_id", pd.Series([1]*len(df))).astype(str)

    # ---------------------------------------------------------
    # DRIVER PERFORMANCE — TOTAL POINTS
    # ---------------------------------------------------------
    st.subheader("🏁 Top Drivers by Total Points")

    driver_points = (
        df.groupby(["driver_id", "driver_name"], dropna=False)["points"]
        .sum()
        .reset_index()
        .sort_values("points", ascending=False)
    )

    fig = px.bar(
        driver_points.head(15),
        x="driver_name",
        y="points",
        title="Top 15 Drivers — Total Points",
        color="points",
        color_continuous_scale="Reds",
    )
    fig.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # DRIVER CONSISTENCY — AVERAGE POINTS PER RACE
    # ---------------------------------------------------------
    st.subheader("📊 Driver Consistency — Avg Points per Race")

    driver_consistency = (
        df.groupby(["driver_id", "driver_name"], dropna=False)["points"]
        .mean()
        .reset_index()
        .rename(columns={"points": "avg_points"})
        .sort_values("avg_points", ascending=False)
    )

    fig2 = px.bar(
        driver_consistency.head(15),
        x="driver_name",
        y="avg_points",
        title="Top 15 Drivers — Average Points per Race",
        color="avg_points",
        color_continuous_scale="Oranges",
    )
    fig2.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # CONSTRUCTOR PERFORMANCE — TOTAL POINTS
    # ---------------------------------------------------------
    st.subheader("🏆 Top Constructors by Total Points")

    constructor_points = (
        df.groupby(["constructor_id", "constructor_name"], dropna=False)["points"]
        .sum()
        .reset_index()
        .sort_values("points", ascending=False)
    )

    fig3 = px.bar(
        constructor_points.head(15),
        x="constructor_name",
        y="points",
        title="Top 15 Constructors — Total Points",
        color="points",
        color_continuous_scale="Blues",
    )
    fig3.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # DRIVER vs CONSTRUCTOR — PERFORMANCE MATRIX
    # ---------------------------------------------------------
    st.subheader("🔗 Driver–Constructor Performance Matrix")

    matrix = (
        df.groupby(["driver_name", "constructor_name"], dropna=False)["points"]
        .sum()
        .reset_index()
    )

    fig4 = px.scatter(
        matrix,
        x="constructor_name",
        y="driver_name",
        size="points",
        color="points",
        title="Driver–Constructor Points Matrix",
        color_continuous_scale="Viridis",
    )
    fig4.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

    # ---------------------------------------------------------
    # SEASON TREND (IF MULTIPLE SEASONS)
    # ---------------------------------------------------------
    if "season" in df.columns and df["season"].nunique() > 1:
        st.subheader("📈 Driver Points Trend Across Seasons")

        season_trend = (
            df.groupby(["season", "driver_name"], dropna=False)["points"]
            .sum()
            .reset_index()
        )

        fig5 = px.line(
            season_trend,
            x="season",
            y="points",
            color="driver_name",
            title="Driver Points Trend Across Seasons",
            markers=True,
        )
        fig5.update_layout(template="plotly_dark")
        st.plotly_chart(fig5, use_container_width=True)

    st.success("RQ1 analysis loaded successfully.")