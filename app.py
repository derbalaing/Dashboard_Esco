import streamlit as st

from pages.dashboard_solar import show_dashboard
import pages.dashboard_par_site as dashboard_par_site
import pages.alerte_solaire as alertes_solaires

st.set_page_config(
    page_title="Solar Monitoring",
    page_icon="☀️",
    layout="wide"
)

st.sidebar.title("Solar Monitoring")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard Global",
        "Analyse Site",
        "Alertes"
    ]
)

if menu == "Dashboard Global":
    show_dashboard()

elif menu == "Analyse Site":
    dashboard_par_site.show()

elif menu == "Alertes":
    alertes_solaires.show()