"""WC 2026 Predictor — Streamlit entry point."""
import os
import streamlit as st

# Copy secrets to env vars for LLM modules
for _key in ("GEMINI_API_KEY", "OPENAI_API_KEY"):
    if _key in st.secrets:
        os.environ[_key] = st.secrets[_key]

st.set_page_config(page_title="WC 2026 Predictor", page_icon="🏆",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, sans-serif; }

    .stApp { background: #f4f6fb; }

    h1 { color: #1a1a2e !important; font-weight: 800 !important; font-size: 2rem !important; letter-spacing: -0.5px; word-break: break-word !important; overflow-wrap: break-word !important; }
    h2 { color: #1a1a2e !important; font-weight: 700 !important; font-size: 1.5rem !important; }
    h3 { color: #1a1a2e !important; font-weight: 600 !important; font-size: 1.2rem !important; }
    h4 { color: #2d2d4e !important; font-weight: 600 !important; }
    p, li, span, div { color: #3d3d5c; }

    .team-card {
        background: white;
        border: 1px solid #e8ecf4;
        border-radius: 14px; padding: 1rem; margin: 0.4rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.15s ease;
    }
    .team-card:hover {
        border-color: #c0c8de;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .team-card strong { color: #1a1a2e; }

    .stMetric {
        background: white; padding: 0.8rem 1.2rem; border-radius: 12px;
        border: 1px solid #e8ecf4; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stMetric label { color: #6b6b8d !important; font-size: 0.8rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.3px; }
    .stMetric [data-testid="stMetricValue"] { color: #1a1a2e !important; font-size: 1.7rem !important; font-weight: 800 !important; }
    .stMetric [data-testid="stMetricDelta"] { color: #8888bb !important; }

    .stButton button {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        color: white; border: none; font-weight: 700; font-size: 0.9rem;
        border-radius: 10px; padding: 0.5rem 1.5rem;
        box-shadow: 0 2px 8px rgba(76,175,80,0.15);
        transition: all 0.15s ease;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #dcedc8, #c5e1a5);
        box-shadow: 0 4px 16px rgba(76,175,80,0.2);
        transform: translateY(-1px);
    }

    .stDataFrame {
        background: white; border-radius: 12px; border: 1px solid #e8ecf4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stDataFrame td { color: #3d3d5c; padding: 0.6rem 0.8rem !important; }
    .stDataFrame th { color: #1a1a2e; background: #f8f9fd; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.3px; }

    .stSelectbox label { color: #3d3d5c !important; font-weight: 500 !important; }
    .stSelectbox div[data-baseweb="select"] { background: white; border: 1px solid #dce0ec; border-radius: 10px; }
    .stSelectbox div[data-baseweb="select"] * { color: #1a1a2e !important; }

    .stMultiSelect label { color: #3d3d5c !important; font-weight: 500 !important; }
    .stSlider label { color: #3d3d5c !important; font-weight: 500 !important; }

    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e8ecf4;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #3d3d5c; padding: 0.4rem 1rem;
        border-radius: 8px; font-weight: 500;
        transition: all 0.1s ease;
    }
    section[data-testid="stSidebar"] .stRadio label:hover { background: #f0f2f8; }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 2px; }

    .stExpander {
        background: white; border: 1px solid #e8ecf4; border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stExpander summary { color: #1a1a2e !important; font-weight: 600 !important; }

    .stSpinner { color: #4361ee; }
    .stSuccess { background: #e8f5e9; border-color: #a5d6a7; color: #2e7d32; }

    a { color: #4361ee; font-weight: 500; }
    a:hover { color: #3a0ca3; }

    hr { border-color: #e8ecf4; margin: 1.5rem 0; }

    section[data-testid="stFileUploader"] { background: white; border: 1px dashed #dce0ec; border-radius: 12px; }

    .stTabs [data-baseweb="tab-list"] { gap: 0; background: #f8f9fd; border-radius: 10px; padding: 3px; }
    .stTabs [data-baseweb="tab"] { color: #6b6b8d; padding: 0.5rem 1.2rem; border-radius: 8px; font-weight: 500; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #1a1a2e; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }

    .match-row {
        background: white; border-radius: 10px; padding: 6px 12px; margin: 3px 0;
        border: 1px solid #e8ecf4; font-size: 0.88rem; color: #3d3d5c;
        transition: all 0.1s ease;
    }
    .match-row:hover { border-color: #c0c8de; }

    .group-team {
        background: white; border-radius: 8px; padding: 5px 12px; margin: 3px 0;
        border-left: 3px solid #4361ee; font-size: 0.9rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    .sidebar-header {
        text-align: center; padding: 1rem 0 0.5rem 0;
    }
    .sidebar-header h1 {
        font-size: 1.6rem !important; color: #4361ee !important; margin: 0;
    }
    .sidebar-header p {
        color: #8888bb; margin-top: -8px; font-size: 0.85rem;
    }
    .sidebar-footer {
        color: #b0b8d0; font-size: 0.8rem;
    }
    .st-emotion-cache-1mi2ry8 { background: white; }
</style>
""", unsafe_allow_html=True)

from dashboard import main

main()
