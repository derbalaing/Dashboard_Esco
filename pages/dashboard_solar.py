import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.database import engine


def show_dashboard():

    st.title("☀️ Dashboard Solaire")

    # ==================================================
    # KPI PRINCIPAUX
    # ==================================================

    query_kpi = """
    SELECT
        COALESCE(SUM(actual_production_kwh),0) AS production,
        COALESCE(SUM(target_kwh),0) AS target
    FROM solar_kpi_daily
    WHERE kpi_date = (
        SELECT MAX(kpi_date)
        FROM solar_kpi_daily
    )
    """

    df_kpi = pd.read_sql(query_kpi, engine)

    production = float(df_kpi.iloc[0]["production"])
    target = float(df_kpi.iloc[0]["target"])

    performance = 0

    if target > 0:
        performance = production / target * 100

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Production",
        f"{production:,.0f} kWh"
    )

    c2.metric(
        "Target",
        f"{target:,.0f} kWh"
    )

    c3.metric(
        "Performance",
        f"{performance:.1f}%"
    )

    st.divider()

    # ==================================================
    # PRODUCTION VS TARGET JOURNALIER
    # ==================================================

    st.subheader(
        "Production Réelle vs Target"
    )

    query_chart = """
    SELECT
        kpi_date,
        SUM(actual_production_kwh) AS production,
        SUM(target_kwh) AS target

    FROM solar_kpi_daily

    GROUP BY kpi_date

    ORDER BY kpi_date
    """

    df_chart = pd.read_sql(
        query_chart,
        engine
    )

    st.write(
        "Nombre de jours :",
        len(df_chart)
    )

    if len(df_chart) > 0:

        df_chart["kpi_date"] = pd.to_datetime(
            df_chart["kpi_date"]
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df_chart["kpi_date"],
                y=df_chart["production"],
                mode="lines",
                name="Production"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_chart["kpi_date"],
                y=df_chart["target"],
                mode="lines",
                name="Target"
            )
        )

        fig.update_layout(
            height=500,
            title="Production Journalière vs Target"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning(
            "Aucune donnée trouvée."
        )

    st.divider()

    # ==================================================
    # GAP MENSUEL
    # ==================================================

    st.subheader(
        "Gap Mensuel"
    )

    query_gap = """
    SELECT

        DATE_TRUNC(
            'month',
            kpi_date
        ) AS month,

        SUM(actual_production_kwh)
            AS production,

        SUM(target_kwh)
            AS target,

        SUM(actual_production_kwh)
            -
        SUM(target_kwh)
            AS gap

    FROM solar_kpi_daily

    GROUP BY
        DATE_TRUNC(
            'month',
            kpi_date
        )

    ORDER BY month
    """

    df_gap = pd.read_sql(
        query_gap,
        engine
    )

    st.write(
        "Nombre de mois :",
        len(df_gap)
    )

    if len(df_gap) > 0:

        fig_gap = go.Figure()

        fig_gap.add_trace(
            go.Bar(
                x=df_gap["month"],
                y=df_gap["gap"],
                name="Gap"
            )
        )

        fig_gap.update_layout(
            height=500,
            title="Gap Mensuel (Production - Target)"
        )

        st.plotly_chart(
            fig_gap,
            use_container_width=True
        )

    else:

        st.warning(
            "Aucune donnée de gap."
        )

    st.divider()

    # ==================================================
    # PRODUCTION / TARGET / GAP
    # ==================================================

    st.subheader(
        "Production / Target / Gap Mensuel"
    )

    if len(df_gap) > 0:

        fig_month = go.Figure()

        fig_month.add_trace(
            go.Bar(
                x=df_gap["month"],
                y=df_gap["production"],
                name="Production"
            )
        )

        fig_month.add_trace(
            go.Bar(
                x=df_gap["month"],
                y=df_gap["target"],
                name="Target"
            )
        )

        fig_month.add_trace(
            go.Scatter(
                x=df_gap["month"],
                y=df_gap["gap"],
                mode="lines+markers",
                name="Gap"
            )
        )

        fig_month.update_layout(
            barmode="group",
            height=600
        )

        st.plotly_chart(
            fig_month,
            use_container_width=True
        )

    st.divider()

    # ==================================================
    # TABLEAU DE CONTROLE
    # ==================================================

    st.subheader(
        "Contrôle données"
    )

    st.dataframe(
        df_chart.tail(20),
        use_container_width=True
    )

