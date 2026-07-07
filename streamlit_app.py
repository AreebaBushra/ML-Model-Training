"""Streamlit Cloud entry point.

Set this file as the main app path in Streamlit Community Cloud:
  Calorie predictions_Multivariate Linear regression/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.app import main

main()
