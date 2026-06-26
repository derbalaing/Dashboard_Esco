import streamlit as st
import pandas as pd

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

    LEFT JOIN solar_alerts a
        ON s.site_id = a.site_id
        AND a.status = 'OPEN'

    ORDER BY
        s.code_site,
        a.alert_date DESC
    """

    df = pd.read_sql(query, engine)

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
        use_container_width=True
    )

    st.download_button(
        "📥 Télécharger Excel",
        df.to_csv(index=False),
        "alertes_sites.csv",
        "text/csv"
    )