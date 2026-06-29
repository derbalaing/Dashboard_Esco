import streamlit as st
import pandas as pd
import io
import plotly.express as px


from config.database import engine


def show():


    st.title("🚨 Alertes Solaires")

    query = """
    SELECT

        s.code_site,
        s.site_name,

        COALESCE(a.alert_type, 'RAS') AS alert_type,

        COALESCE(a.severity, 'RAS') AS severity,

        COALESCE(a.description, 'Aucune alerte') AS description,

        a.alert_date

    FROM solar_installations si

    INNER JOIN sites s
        ON si.site_id = s.site_id

    LEFT JOIN (

        SELECT DISTINCT ON (site_id)

            alert_id,
            site_id,
            alert_date,
            alert_type,
            severity,
            description,
            status

        FROM solar_alerts

        WHERE status = 'OPEN'

        ORDER BY

            site_id,

            CASE UPPER(TRIM(severity))

                WHEN 'CRITICAL' THEN 1
                WHEN 'MAJOR' THEN 2
                WHEN 'MINOR' THEN 3
                ELSE 4

            END,

            alert_date DESC

    ) a

    ON s.site_id = a.site_id

    ORDER BY
        s.code_site,
        a.alert_date DESC
    """

    df = pd.read_sql(query, engine)




    # =====================================================
    # CAMEMBERT
    # =====================================================

    st.subheader("Répartition des alertes par type")

    pie = (
        df.groupby("alert_type")
        .size()
        .reset_index(name="Nombre")
    )

    fig = px.pie(
        pie,
        names="alert_type",
        values="Nombre",
        hole=0.35
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # FILTRE TYPE ALERTE
    # =====================================================

    types_alertes = ["Toutes"] + sorted(
        df["alert_type"].dropna().unique().tolist()
    )

    type_selection = st.selectbox(
        "Filtrer par type d'alerte",
        types_alertes
    )

    if type_selection != "Toutes":
        df = df[df["alert_type"] == type_selection]

    

    st.metric(
        "Sites Solarisés",
        df["code_site"].nunique()
    )

    st.metric(
        "Alertes Ouvertes",
        len(df[df["severity"] != "RAS"])
    )

    st.divider()

    def color_alert(row):

        severity = str(row["severity"]).strip().upper()

        if severity == "CRITICAL":
            return [
                "background-color:#ffcccc"
            ] * len(row)

        elif severity == "MAJOR":
            return [
                "background-color:#ffe0b3"
            ] * len(row)

        elif severity == "MINOR":
            return [
                "background-color:#fff2cc"
            ] * len(row)

        else:
            return [
                "background-color:#d9ead3"
            ] * len(row)

    st.dataframe(
        df.style.apply(
            color_alert,
            axis=1
        ),
        use_container_width=True,
        height=720
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Alertes"
        )

    buffer.seek(0)

    st.download_button(
        label="📥 Télécharger Excel",
        data=buffer,
        file_name="alertes_sites.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    df["severity"] = (
    df["severity"]
    .fillna("RAS")
    .astype(str)
    .str.strip()
    .str.upper()
    )

    pie = (
        df.groupby("severity")
        .size()
        .reset_index(name="Nombre")
    )
    
    fig = px.pie(
        pie,
        names="severity",
        values="Nombre",
        title="Répartition des alertes par criticité",
        hole=0.4
    )

    st.plotly_chart(
    fig,
    use_container_width=True
    )
