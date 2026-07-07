from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go
import requests
import streamlit as st

from frontend.api_client import get_client
from frontend.history_store import (
    delete_history,
    history_stats,
    load_history,
    save_prediction,
)
from frontend.ui_helpers import inject_css, load_metadata, metric_card

st.set_page_config(
    page_title="Calorie Burn Predictor",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

ROOT = Path(__file__).resolve().parents[1]
METADATA = load_metadata()
METRICS = METADATA.get("metrics", {})


def check_api_status() -> tuple[bool, str]:
    try:
        client = get_client()
        data = client.health()
        if data.get("status") == "ok" and data.get("model_loaded"):
            return True, "API Online • Model Ready"
        return False, "API Online • Model Not Loaded"
    except Exception:
        return False, "API Offline"


def render_gauge(calories: float) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=calories,
            title={"text": "Predicted Calories (kcal)", "font": {"size": 20}},
            number={"suffix": " kcal", "font": {"size": 42}},
            gauge={
                "axis": {"range": [0, max(400, calories * 1.2)]},
                "bar": {"color": "#6366f1"},
                "steps": [
                    {"range": [0, 100], "color": "#e0e7ff"},
                    {"range": [100, 200], "color": "#c7d2fe"},
                    {"range": [200, 400], "color": "#a5b4fc"},
                ],
                "threshold": {
                    "line": {"color": "#ec4899", "width": 4},
                    "thickness": 0.8,
                    "value": calories,
                },
            },
        )
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


def page_home() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <h1>🔥 Calorie Burn Intelligence Dashboard</h1>
            <p>Predict workout calorie expenditure using the same multivariate linear regression
            model trained on 750,000 exercise records.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    online, status_text = check_api_status()
    pill_class = "status-online" if online else "status-offline"
    st.markdown(
        f'<span class="status-pill {pill_class}">{status_text}</span>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Algorithm", "Linear Regression", "🧠")
    with c2:
        metric_card("R² Score", f"{METRICS.get('r2_score', 0):.3f}", "📈")
    with c3:
        metric_card("RMSE", f"{METRICS.get('rmse', 0):.2f}", "📉")
    with c4:
        metric_card("MAE", f"{METRICS.get('mae', 0):.2f}", "🎯")

    st.markdown("### Quick Start")
    st.markdown(
        """
        1. Open **Prediction** in the sidebar and enter your workout details.
        2. Click **Predict** to call the FastAPI model endpoint.
        3. Review calories, BMI, intensity, and personalized tips.
        4. Track sessions in **History** and export your log anytime.
        """
    )

    history_df = load_history()
    stats = history_stats(history_df)
    st.markdown("### Your Activity Snapshot")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Predictions", stats["total_predictions"])
    s2.metric("Avg Calories", stats["avg_calories"])
    s3.metric("Avg Duration (min)", stats["avg_duration"])
    s4.metric("Avg BMI", stats["avg_bmi"])


def page_prediction() -> None:
    st.markdown("## 🏋️ Workout Prediction")
    st.caption("Enter your session details — predictions use the notebook's exact feature order and preprocessing.")

    online, _ = check_api_status()
    if not online:
        st.error("FastAPI backend is not reachable. Start it with: `uvicorn backend.app:app --reload`")
        return

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["male", "female"])
            age = st.number_input("Age", min_value=10, max_value=100, value=30)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1.0, max_value=300.0, value=30.0, step=0.5)
            heart_rate = st.number_input("Heart Rate (bpm)", min_value=50.0, max_value=220.0, value=120.0, step=1.0)
            body_temp = st.number_input("Body Temperature (°C)", min_value=35.0, max_value=42.0, value=39.5, step=0.1)

        submitted = st.form_submit_button("🔮 Predict Calories", use_container_width=True, type="primary")

    if submitted:
        payload = {
            "gender": gender,
            "age": int(age),
            "height": float(height),
            "weight": float(weight),
            "duration": float(duration),
            "heart_rate": float(heart_rate),
            "body_temp": float(body_temp),
        }

        with st.spinner("Calling prediction API..."):
            try:
                result = get_client().predict(payload)
                save_prediction(payload, result)
                st.session_state["last_prediction"] = result
                st.session_state["last_inputs"] = payload
                st.success("Prediction complete!")
            except RuntimeError as exc:
                st.error(f"Prediction failed: {exc}")
                return
            except Exception as exc:
                st.error(f"Could not reach API: {exc}")
                return

    if "last_prediction" in st.session_state:
        result = st.session_state["last_prediction"]
        st.markdown("---")
        st.markdown("### Results")

        m1, m2, m3 = st.columns(3)
        with m1:
            metric_card("Calories Burned", f"{result['predicted_calories']:.0f} kcal", "🔥")
        with m2:
            metric_card("BMI", f"{result['bmi']} ({result['bmi_category']})", "⚖️")
        with m3:
            metric_card(
                "Workout Intensity",
                f"{result['workout_intensity']} ({result['intensity_score']}%)",
                "💓",
            )

        chart_col, info_col = st.columns([1.1, 1])
        with chart_col:
            render_gauge(result["predicted_calories"])
        with info_col:
            st.markdown("#### Personalized Suggestions")
            for tip in result["suggestions"]:
                st.markdown(f"- {tip}")

            st.markdown("#### Equivalent Activities")
            for item in result["equivalent_activities"]:
                st.markdown(
                    f"- **{item['activity']}**: ~{item['duration_minutes']} min"
                )

        st.markdown(
            f"""
            <div class="summary-card">
                <strong>Summary</strong><br>{result['summary']}
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_history() -> None:
    st.markdown("## 📜 Prediction History")
    df = load_history()

    if df.empty:
        st.info("No predictions saved yet. Make your first prediction on the Prediction page.")
        return

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="predictions_history.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        if st.button("🗑️ Delete History", use_container_width=True):
            delete_history()
            st.warning("History cleared.")
            st.rerun()

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### Trends")
    chart_df = df.copy().sort_values("timestamp")
    st.line_chart(chart_df.set_index("timestamp")["predicted_calories"])


def page_model_info() -> None:
    st.markdown("## 🧪 Model Information")
    st.caption("Metrics and configuration extracted from the training notebook.")

    if not METADATA:
        st.warning("model_metadata.json not found. Run `python scripts/export_model.py` first.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Overview")
        st.markdown(
            f"""
            | Field | Value |
            |---|---|
            | **Algorithm** | {METADATA.get('algorithm', 'N/A')} |
            | **Dataset** | {METADATA.get('dataset', 'N/A')} |
            | **Author** | {METADATA.get('author', 'N/A')} |
            """
        )
    with c2:
        st.markdown("### Performance (validation set)")
        st.metric("R² Score", f"{METRICS.get('r2_score', 0):.4f}")
        st.metric("RMSE", f"{METRICS.get('rmse', 0):.4f}")
        st.metric("MAE", f"{METRICS.get('mae', 0):.4f}")

    st.markdown("### Features (exact notebook order)")
    features = METADATA.get("feature_order", METADATA.get("features", []))
    for idx, feature in enumerate(features, start=1):
        st.markdown(f"{idx}. `{feature}`")

    st.markdown("### Preprocessing")
    st.markdown(
        """
        <div class="info-box">
        <strong>Gender encoding:</strong> male = 1, female = 0<br>
        <strong>Scaling:</strong> None (raw features, matching the notebook)<br>
        <strong>Split:</strong> 80/20 train-validation, random_state=3<br>
        <strong>Post-processing:</strong> Negative predictions clipped to 1 kcal (notebook limitation note)
        </div>
        """,
        unsafe_allow_html=True,
    )

    with open(ROOT / "backend" / "model_metadata.json", encoding="utf-8") as file:
        st.expander("Raw metadata JSON").code(json.dumps(json.load(file), indent=2))


def page_about() -> None:
    st.markdown("## ℹ️ About")
    st.markdown(
        """
        This production app wraps the **Calorie Expenditure Prediction** notebook by **Areeba Bushra**,
        converting a Colab-trained multivariate linear regression workflow into a deployable
        FastAPI + Streamlit stack.

        ### Architecture
        - **Backend:** FastAPI loads `model.pkl` once at startup and serves `/health` and `/predict`.
        - **Frontend:** Streamlit dashboard calls the API and persists predictions to `data/predictions_history.csv`.
        - **Model:** scikit-learn `LinearRegression` on 7 features with R² ≈ 0.968 on the validation split.

        ### Repository
        [ML-Model-Training — Calorie predictions](https://github.com/AreebaBushra/ML-Model-Training/tree/82e0affa4acad8c1e05e0d9324120d00864dc560/Calorie%20predictions_Multivariate%20Linear%20regression)

        ### How to run
        ```bash
        pip install -r requirements.txt
        uvicorn backend.app:app --reload
        streamlit run frontend/app.py
        ```
        """
    )


PAGES = {
    "Home": page_home,
    "Prediction": page_prediction,
    "History": page_history,
    "Model Information": page_model_info,
    "About": page_about,
}

with st.sidebar:
    st.markdown("## 🔥 FitMetrics AI")
    st.caption("Calorie Prediction Dashboard")
    selection = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("---")
    online, status = check_api_status()
    st.markdown(f"**Status:** {status}")

PAGES[selection]()
