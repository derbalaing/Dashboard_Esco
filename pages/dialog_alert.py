from sqlalchemy import text
from config.database import engine
import streamlit as st

@st.dialog("Gestion de l'alerte")
def dialog_alert(site_id):

    st.write("Site :", site_id)

    alert_type = st.selectbox(
        "Type",
        [
            "LOW_PRODUCTION",
            "NO_PRODUCTION",
            "LOSTCOM",
            "Information"
        ]
    )

    severity = st.selectbox(
        "Criticité",
        [
            "CRITICAL",
            "MAJOR",
            "MINOR",
            "INFO"
        ]
    )

    valeur = st.number_input(
        "Valeur",
        value=0.0
    )

    description = st.text_area(
        "Description"
    )

    status = st.selectbox(
        "Status",
        [
            "OPEN",
            "CLOSED"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:



        if st.button("💾 Enregistrer"):

            sql = text("""
                INSERT INTO solar_alerts
                (
                    site_id,
                    alert_date,
                    alert_type,
                    severity,
                    value,
                    description,
                    status,
                    created_at
                )

                VALUES
                (
                    :site_id,
                    CURRENT_DATE,
                    :alert_type,
                    :severity,
                    :value,
                    :description,
                    :status,
                    NOW()
                )
            """)

            try:

                with engine.begin() as conn:

                    conn.execute(
                        sql,
                        {
                            "site_id": site_id,
                            "alert_type": alert_type,
                            "severity": severity,
                            "value": valeur,
                            "description": description,
                            "status": status
                        }
                    )

                st.success("✅ Alerte enregistrée avec succès.")

                st.rerun()

            except Exception as e:

                st.error(e)

    with col2:

        if st.button("❌ Annuler"):

            st.rerun()