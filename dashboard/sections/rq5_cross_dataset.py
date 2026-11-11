import streamlit as st
import plotly.express as px
import pandas as pd

def render_rq5(data):
    st.title("🔗 RQ5 — Cross‑Dataset Insights")

    results = data["results"].copy()
    races = data.get("races", pd.DataFrame()).copy()
    circuits = data.get("circuits", pd.DataFrame()).copy()

    if results.empty:
        st.warning("⚠️ No records match your current filter settings. Broaden your sidebar filters.")
        return

    df = results.copy()

    # Merge circuit names across multi-season records via races (season + round)
    if not races.empty and "season" in df.columns and "round" in df.columns and "season" in races.columns and "round" in races.columns:
        races_subset = races.copy()
        for name_col in ["circuit_name", "name", "circuitRef", "race_name"]:
            if name_col in races_subset.columns:
                races_subset["circuit_name"] = races_subset[name_col]
                break
        df = df.merge(
            races_subset[["season", "round", "circuit_name" if "circuit_name" in races_subset.columns else "round"]].drop_duplicates(subset=["season", "round"]),
            on=["season", "round"],
            how="left",
            suffixes=("", "_races")
        )
        if "circuit_name_races" in df.columns:
            df["circuit_name"] = df["circuit_name"].fillna(df["circuit_name_races"])

    if "circuit_name" in df.columns:
        df["circuit_name"] = df["circuit_name"].fillna("Grand Prix Circuit")
    else:
        df["circuit_name"] = "Grand Prix Circuit"

    if "driver_name" not in df.columns:
        df["driver_name"] = "Driver " + df.get("driver_id", pd.Series([1]*len(df))).astype(str)

    if "constructor_name" not in df.columns:
        df["constructor_name"] = "Constructor " + df.get("constructor_id", pd.Series([1]*len(df))).astype(str)

    # 1. Weighted Performance Index
    st.subheader("🔥 Weighted Performance Index (Race + Sprint)")

    final_col = "final_position" if "final_position" in df.columns else "position"
    df["is_win"] = (df[final_col] == 1).astype(int)
    df["is_podium"] = (df[final_col] <= 3).astype(int)

    df["performance_index"] = (
        df["points"]
        + df["is_win"] * 10
        + df["is_podium"] * 5
    )

    perf = (
        df.groupby("driver_name", dropna=False)["performance_index"]
        .sum()
        .reset_index()
        .sort_values("performance_index", ascending=False)
    )

    fig = px.bar(
        perf.head(15),
        x="driver_name",
        y="performance_index",
        title="Top Drivers by Weighted Performance Index",
        color="performance_index",
        color_continuous_scale="Teal",
    )
    fig.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # 2. Driver–Circuit Performance Matrix
    st.subheader("🌍 Driver–Circuit Performance Matrix")

    top_drivers = df.groupby("driver_name")["points"].sum().nlargest(15).index
    top_circuits = df.groupby("circuit_name")["points"].sum().nlargest(15).index

    filtered_matrix_df = df[df["driver_name"].isin(top_drivers) & df["circuit_name"].isin(top_circuits)]

    if not filtered_matrix_df.empty:
        circuit_matrix = (
            filtered_matrix_df.groupby(["driver_name", "circuit_name"], dropna=False)["points"]
            .sum()
            .reset_index()
        )

        fig2 = px.density_heatmap(
            circuit_matrix,
            x="circuit_name",
            y="driver_name",
            z="points",
            title="Driver–Circuit Points Heatmap",
            color_continuous_scale="Magma",
        )
        fig2.update_layout(template="plotly_dark", xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Constructor–Circuit Synergy
    st.subheader("🏗️ Constructor–Circuit Synergy")

    if not filtered_matrix_df.empty:
        constructor_circuit = (
            filtered_matrix_df.groupby(["constructor_name", "circuit_name"], dropna=False)["points"]
            .sum()
            .reset_index()
        )

        fig3 = px.scatter(
            constructor_circuit,
            x="circuit_name",
            y="constructor_name",
            size="points",
            color="points",
            title="Constructor–Circuit Synergy (Points)",
            color_continuous_scale="Viridis",
        )
        fig3.update_layout(template="plotly_dark", xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)

    # 4. Nationality Performance
    st.subheader("🌎 Nationality‑Based Performance")

    nat_col = "driver_nationality" if "driver_nationality" in df.columns else ("nationality" if "nationality" in df.columns else None)
    if nat_col:
        nationality_perf = (
            df.groupby(nat_col, dropna=False)["points"]
            .sum()
            .reset_index()
            .sort_values("points", ascending=False)
        )

        fig4 = px.bar(
            nationality_perf,
            x=nat_col,
            y="points",
            title="Driver Nationality — Total Points",
            color="points",
            color_continuous_scale="Inferno",
        )
        fig4.update_layout(template="plotly_dark", xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

    # 5. Season Trend
    st.subheader("📈 Season‑Wise Performance Trend")

    if "season" in df.columns:
        season_trend = (
            df.groupby("season", dropna=False)["points"]
            .sum()
            .reset_index()
            .sort_values("season")
        )

        fig5 = px.line(
            season_trend,
            x="season",
            y="points",
            title="Total Points Awarded per Season",
            markers=True,
            color_discrete_sequence=["#ff1e00"],
        )
        fig5.update_layout(template="plotly_dark")
        st.plotly_chart(fig5, use_container_width=True)

    st.success("RQ5 analysis loaded successfully.")