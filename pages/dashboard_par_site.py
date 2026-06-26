import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config.database import engine


def show():

    st.title("☀️ Analyse Solaire par Site")

    # ==================================================
    # LISTE DES SITES
    # ==================================================

    sites = pd.read_sql(
        """
        SELECT
            site_id,
            code_site,
            site_name
        FROM sites
        ORDER BY code_site
        """,
        engine
    )

    site_selected = st.selectbox(
        "Choisir un site",
        sites["code_site"]
    )

    site_id = sites.loc[
        sites["code_site"] == site_selected,
        "site_id"
    ].iloc[0]

    # ==================================================
    # INFOS SITE
    # ==================================================

    query_site = f"""
    SELECT
        s.code_site,
        s.site_name,
        si.panel_type,
        si.panel_power_wc,
        si.panel_quantity,
        si.ipv_efficiency

    FROM sites s

    LEFT JOIN solar_installations si
        ON s.site_id = si.site_id

    WHERE s.site_id = {site_id}
    """

    df_site = pd.read_sql(
        query_site,
        engine
    )

    if not df_site.empty:

        row = df_site.iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Site",
            row["code_site"]
        )

        c2.metric(
            "Panneaux",
            row["panel_quantity"]
        )

        c3.metric(
            "Puissance panneau",
            f"{row['panel_power_wc']} W"
        )

        c4.metric(
            "IPV Efficiency",
            f"{row['ipv_efficiency']} %"
        )

    st.divider()

    # ==================================================
    # KPI SITE
    # ==================================================

    query_kpi = f"""
    SELECT
        SUM(actual_production_kwh) AS production,
        SUM(target_kwh) AS target

    FROM solar_kpi_daily

    WHERE site_id = {site_id}
    """

    df_kpi = pd.read_sql(
        query_kpi,
        engine
    )

    production = float(df_kpi.iloc[0]["production"] or 0)
    target = float(df_kpi.iloc[0]["target"] or 0)

    performance = 0

    if target > 0:
        performance = production / target * 100

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Production Totale",
        f"{production:,.0f} kWh"
    )

    c2.metric(
        "Target Total",
        f"{target:,.0f} kWh"
    )

    c3.metric(
        "Performance",
        f"{performance:.1f}%"
    )

    st.divider()

    # ==================================================
    # ALERTES
    # ==================================================

    st.subheader("🚨 Alertes Actives")

    try:

        query_alerts = f"""
        SELECT
            alert_date,
            alert_type,
            severity,
            description

        FROM solar_alerts

        WHERE site_id = {site_id}
        AND status = 'OPEN'

        ORDER BY alert_date DESC
        """

        df_alerts = pd.read_sql(
            query_alerts,
            engine
        )

        if df_alerts.empty:

            st.success(
                "Aucune alerte active"
            )

        else:

            for _, row in df_alerts.iterrows():

                severity = str(
                    row["severity"]
                ).upper()

                message = (
                    f"{row['alert_type']} - "
                    f"{row['description']}"
                )

                if severity == "CRITICAL":

                    st.error(
                        f"🔴 {message}"
                    )

                elif severity == "MAJOR":

                    st.warning(
                        f"🟠 {message}"
                    )

                elif severity == "MINOR":

                    st.info(
                        f"🟡 {message}"
                    )

                else:

                    st.info(
                        f"🔵 {message}"
                    )

    except Exception as e:

        st.error(
            f"Erreur alertes : {e}"
        )

    st.divider()

    # ==================================================
    # COURBE JOURNALIERE
    # ==================================================

    query_chart = f"""
    SELECT

        kpi_date,
        actual_production_kwh,
        target_kwh,
        variance_kwh,
        status

    FROM solar_kpi_daily

    WHERE site_id = {site_id}

    ORDER BY kpi_date
    """

    df = pd.read_sql(
        query_chart,
        engine
    )

    if not df.empty:

        df["kpi_date"] = pd.to_datetime(
            df["kpi_date"]
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["kpi_date"],
                y=df["actual_production_kwh"],
                name="Production Réelle"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["kpi_date"],
                y=df["target_kwh"],
                name="Target"
            )
        )

        fig.update_layout(
            title=f"{site_selected} - Production vs Target",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        # ==================================================
        # GAP
        # ==================================================

        fig_gap = go.Figure()

        fig_gap.add_trace(
            go.Bar(
                x=df["kpi_date"],
                y=df["variance_kwh"],
                name="Gap"
            )
        )

        fig_gap.update_layout(
            title="Gap Journalier",
            height=500
        )

        st.plotly_chart(
            fig_gap,
            use_container_width=True
        )

        st.divider()

        # ==================================================
        # LOSTCOM
        # ==================================================

        st.subheader(
            "Historique LostCom"
        )

        lostcom = df[
            df["status"] == "LOSTCOM"
        ]

        st.dataframe(
            lostcom,
            use_container_width=True
        )

        st.divider()

        # ==================================================
        # LOW PRODUCTION
        # ==================================================

        st.subheader(
            "Historique Faible Production"
        )

        low_prod = df[
            df["status"] == "LOW_PRODUCTION"
        ]

        st.dataframe(
            low_prod,
            use_container_width=True
        )