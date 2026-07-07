import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "backend" / "model_metadata.json"


def load_metadata() -> dict:
    if METADATA_PATH.exists():
        with open(METADATA_PATH, encoding="utf-8") as file:
            return json.load(file)
    return {}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }

        .hero-card {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            border-radius: 20px;
            padding: 2rem 2.2rem;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 20px 45px rgba(99, 102, 241, 0.25);
        }

        .hero-card h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
            font-weight: 700;
        }

        .hero-card p {
            margin: 0;
            opacity: 0.95;
            font-size: 1.05rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            height: 100%;
        }

        .metric-card h3 {
            margin: 0 0 0.35rem 0;
            color: #64748b;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .metric-card h2 {
            margin: 0;
            color: #0f172a;
            font-size: 1.8rem;
            font-weight: 700;
        }

        .summary-card {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0f9ff 100%);
            border: 1px solid #bae6fd;
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            margin-top: 1rem;
        }

        .status-pill {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .status-online {
            background: #dcfce7;
            color: #166534;
        }

        .status-offline {
            background: #fee2e2;
            color: #991b1b;
        }

        .info-box {
            background: #f8fafc;
            border-left: 4px solid #6366f1;
            padding: 1rem 1.2rem;
            border-radius: 0 12px 12px 0;
            margin: 0.8rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>{icon} {label}</h3>
            <h2>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
