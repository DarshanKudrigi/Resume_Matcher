def get_css() -> str:
    return """
<style>
    /* ── Main app ── */
    .stApp { background-color: #0f1117; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #1a1d2e;
        border-right: 1px solid #2d2f3e;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] strong,
    [data-testid="stSidebar"] span {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #c0c4d6 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #3d4060 !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3d4060;
        border-radius: 12px;
        padding: 20px;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #7c83ff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9098b1 !important;
        font-size: 0.85rem !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
        color: #ffffff !important;
    }

    /* ── Clear button specific ── */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background-color: #2d2f3e !important;
        border: 1px solid #e05c5c !important;
        color: #e05c5c !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background-color: #e05c5c !important;
        color: #ffffff !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Main header ── */
    .main-header {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #3d4060;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }
    .main-sub {
        color: #9098b1;
        font-size: 1rem;
        margin-top: 0.3rem;
    }

    /* ── Tech badges ── */
    .badge {
        display: inline-block;
        background: #2d3250;
        border: 1px solid #7c83ff;
        color: #7c83ff;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 8px;
    }

    /* ── Section titles ── */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3d4060;
    }

    /* ── General text ── */
    .stMarkdown p {
        color: #c0c4d6;
    }
    p, span, label {
        color: #c0c4d6;
    }

    /* ── All widget labels ── */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    label {
        color: #c0c4d6 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    /* ── Selectbox text ── */
    [data-testid="stSelectbox"] div,
    [data-testid="stSelectbox"] span,
    [data-testid="stSelectbox"] p {
        color: #e0e0e0 !important;
    }

    /* ── Multiselect text ── */
    [data-testid="stMultiSelect"] span,
    [data-testid="stMultiSelect"] p,
    [data-testid="stMultiSelect"] div {
        color: #e0e0e0 !important;
    }

    /* ── Slider label ── */
    [data-testid="stSlider"] label,
    [data-testid="stSlider"] p {
        color: #c0c4d6 !important;
    }
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"] {
        color: #9098b1 !important;
    }

    /* ── Caption ── */
    [data-testid="stCaptionContainer"] p {
        color: #9098b1 !important;
        font-size: 0.85rem !important;
    }

    /* ── Info box ── */
    [data-testid="stAlert"] {
        background-color: #1e2130 !important;
        border: 1px solid #3d4060 !important;
        color: #c0c4d6 !important;
        border-radius: 10px !important;
    }

    /* ── Success message ── */
    [data-testid="stAlert"][kind="success"] {
        background-color: #1a2e22 !important;
        border: 1px solid #4caf82 !important;
        color: #4caf82 !important;
    }

    /* ── Input fields background ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background-color: #1e2130 !important;
        border: 1px solid #3d4060 !important;
        border-radius: 8px !important;
    }

    /* ── Update button special styling ── */
    .update-btn > button {
        background-color: #7c83ff !important;
        color: #ffffff !important;
        border: none !important;
    }
    .update-btn > button:hover {
        background-color: #5c64ff !important;
    }
</style>
"""