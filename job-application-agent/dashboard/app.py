import streamlit as st
import pandas as pd

from main import run_pipeline
from tracker.sheets_tracker import clear_sheet, get_sheet
from dashboard.styles import get_css
from dashboard.components import (
    render_header,
    render_sidebar,
    render_metrics,
    render_charts,
    render_job_table,
    render_status_updater,
)


def load_data() -> pd.DataFrame:
    sheet = get_sheet()
    data = sheet.get_all_records()
    return pd.DataFrame(data)


# ── App setup ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(get_css(), unsafe_allow_html=True)
render_sidebar(run_callback=run_pipeline, clear_callback=lambda: clear_sheet(confirm=True))
render_header()

# ── Data ──────────────────────────────────────────────────────
try:
    df = load_data()

    if df.empty:
        st.info("No jobs logged yet. Click **▶ Run Agent Now** in the sidebar.")
        st.stop()

    if "Match Score" in df.columns:
        df["Score_num"] = pd.to_numeric(
            df["Match Score"].astype(str).str.replace("%", "", regex=False),
            errors="coerce"
        ).fillna(0.0)
    else:
        df["Score_num"] = 0.0

    render_metrics(df)
    st.markdown("<br>", unsafe_allow_html=True)
    render_charts(df)
    st.markdown("<br>", unsafe_allow_html=True)
    render_job_table(df)
    st.markdown("<br>", unsafe_allow_html=True)
    render_status_updater(df)

except Exception as e:
    st.error(f"Could not load data: {e}")