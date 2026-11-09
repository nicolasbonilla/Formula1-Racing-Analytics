import streamlit as st
import plotly.express as px
import pandas as pd

def render_rq3(df: pd.DataFrame):
    """
    RQ3 - Circuit Geography & Regional Performance section.
    """
    st.header("🌎 RQ3 — Circuit Geography & Regional Performance")
    
    if df.empty:
        st.warning("⚠️ No data available matching the current filter criteria.")
        return

    # Debug helper or column resolver
    # Standardize column names dynamically based on what's available in the merged df
    country_col = next((c for c in ["circuit_country", "country", "location", "locality"] if c in df.columns), None)
    circuit_col = next((c for c in ["circuit_name", "name", "circuitRef"] if c in df.columns), None)
    driver_col = next((c for c in ["driver_name", "surname", "driverRef", "family_name"] if c in df.columns), None)
    
    # Fallback column mapping if standard Ergast/Gold names are split
    if not country_col and "location" in df.columns:
        country_col = "location"
    if not country_col:
        # Create a dummy country column if missing to prevent crashes
        df["circuit_country"] = "Unknown"
        country_col = "circuit_country"

    if not circuit_col:
        df["circuit_name"] = "Unknown Circuit"
        circuit_col = "circuit_name"

    if not driver_col:
        df["driver_name"] = "Driver"
        driver_col = "driver_name"

    # ---------------------------------------------------------
    # 1. READ SIDEBAR FILTERS
    # ---------------------------------------------------------
    selected_seasons = st.session_state.get("selected_seasons", [])
    grid_range = st.session_state.get("grid_range", (1, 20))
    pos_range = st.session_state.get("pos_range", (1, 20))
    points_range = st.session_state.get("points_range", (0, 30))

    df_filtered = df.copy()

    # Apply Season Filter
    if selected_seasons and "season" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["season"].isin(selected_seasons)]

    # Apply Position/Points Filters safely
    if "grid_position" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["grid_position"].between(grid_range[0], grid_range[1])]
    elif "grid" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["grid"].between(grid_range[0], grid_range[1])]

    if "final_position" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["final_position"].between(pos_range[0], pos_range[1])]
    elif "position" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["position"].between(pos_range[0], pos_range[1])]

    if "points" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["points"].between(points_range[0], points_range[1])]

    if df_filtered.empty:
        st.warning("⚠️ No records match your current filter settings. Please broaden your slider or season selections.")
        return

    # ---------------------------------------------------------
    # 2. CIRCUIT PERFORMANCE BY COUNTRY
    # ---------------------------------------------------------
    st.subheader("🗺️ Circuit Performance by Country")

    country_df = (
        df_filtered.groupby(country_col, as_index=False)["points"]
        .sum()
        .sort_values(by="points", ascending=False)
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        fig_map = px.choropleth(
            country_df,
            locations=country_col,
            locationmode="country names",
            color="points",
            color_continuous_scale="Viridis",
            title="Circuit Performance — Points by Host Country",
            labels={country_col: "Country", "points": "Total Points"}
        )
        fig_map.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        fig_country_bar = px.bar(
            country_df.head(15),
            x=country_col,
            y="points",
            color="points",
            color_continuous_scale="Plasma",
            title="Total Points Awarded by Country (Top 15)",
            labels={country_col: "Country", "points": "Points"}
        )
        fig_country_bar.update_layout(template="plotly_dark", xaxis_tickangle=-45)
        st.plotly_chart(fig_country_bar, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. CIRCUIT COMPETITIVENESS INDEX (CCI)
    # ---------------------------------------------------------
    st.subheader("🔥 Circuit Competitiveness Index (CCI)")
    st.caption("Lower CCI score indicates tighter grid performance and higher position variance.")

    g_col = "grid_position" if "grid_position" in df_filtered.columns else "grid"
    p_col = "final_position" if "final_position" in df_filtered.columns else "position"

    if g_col in df_filtered.columns and p_col in df_filtered.columns:
        df_filtered["pos_delta"] = (df_filtered[g_col] - df_filtered[p_col]).abs()
        
        cci_df = (
            df_filtered.groupby(circuit_col, as_index=False)["pos_delta"]
            .mean()
            .rename(columns={"pos_delta": "competitiveness"})
            .sort_values(by="competitiveness", ascending=True)
        )

        fig_cci = px.bar(
            cci_df.head(15),
            x=circuit_col,
            y="competitiveness",
            color="competitiveness",
            color_continuous_scale="Turbo",
            title="Circuit Competitiveness Index (Lower = Tighter Racing)",
            labels={circuit_col: "Circuit", "competitiveness": "CCI Score"}
        )
        fig_cci.update_layout(template="plotly_dark", xaxis_tickangle=-45)
        st.plotly_chart(fig_cci, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 4. DRIVER-CIRCUIT AFFINITY HEATMAP
    # ---------------------------------------------------------
    st.subheader("🏎️ Driver–Circuit Affinity Heatmap")

    if driver_col in df_filtered.columns and circuit_col in df_filtered.columns:
        top_drivers = df_filtered.groupby(driver_col)["points"].sum().nlargest(15).index
        top_circuits = df_filtered.groupby(circuit_col)["points"].sum().nlargest(15).index

        affinity_df = df_filtered[
            df_filtered[driver_col].isin(top_drivers) & df_filtered[circuit_col].isin(top_circuits)
        ]

        if not affinity_df.empty:
            heatmap_data = (
                affinity_df.groupby([driver_col, circuit_col], as_index=False)["points"]
                .sum()
            )

            fig_heatmap = px.density_heatmap(
                heatmap_data,
                x=circuit_col,
                y=driver_col,
                z="points",
                color_continuous_scale="Magma",
                title="Driver–Circuit Affinity (Points Scored)",
                labels={circuit_col: "Circuit", driver_col: "Driver", "points": "Points"}
            )
            fig_heatmap.update_layout(template="plotly_dark", xaxis_tickangle=-45)
            st.plotly_chart(fig_heatmap, use_container_width=True)