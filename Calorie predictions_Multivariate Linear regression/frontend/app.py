from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.api_client import get_client
from frontend.history_store import (
    delete_history,
    history_stats,
    load_history,
    save_prediction,
)
from frontend.local_predictor import is_model_ready, predict_locally
from frontend.ui_helpers import inject_css, load_metadata, metric_card


def run_prediction(payload: dict) -> dict:
    """Use FastAPI when CALORIE_API_URL is set and reachable; otherwise predict locally."""
    api_url = os.getenv("CALORIE_API_URL")
    if api_url:
        try:
            return get_client(api_url).predict(payload)
        except Exception:
            pass
    return predict_locally(payload)


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


def page_home(metrics: dict) -> None:
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

    ready, status_text = is_model_ready()
    pill_class = "status-online" if ready else "status-offline"
    st.markdown(
        f'<span class="status-pill {pill_class}">{status_text}</span>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Algorithm", "Linear Regression", "🧠")
    with c2:
        metric_card("R² Score", f"{metrics.get('r2_score', 0):.3f}", "📈")
    with c3:
        metric_card("RMSE", f"{metrics.get('rmse', 0):.2f}", "📉")
    with c4:
        metric_card("MAE", f"{metrics.get('mae', 0):.2f}", "🎯")

    st.markdown("### Quick Start")
    st.markdown(
        """
        1. Open **Prediction** in the sidebar and enter your workout details.
        2. Click **Predict** to run the trained model.
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

    ready, status = is_model_ready()
    if not ready:
        st.error(f"Model is not available: {status}")
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

        with st.spinner("Running prediction..."):
            try:
                result = run_prediction(payload)
                save_prediction(payload, result)
                st.session_state["last_prediction"] = result
                st.session_state["last_inputs"] = payload
                st.success("Prediction complete!")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")
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


def page_model_info(metadata: dict, metrics: dict) -> None:
    st.markdown("## 🧪 Model Information")
    st.caption("Metrics and configuration extracted from the training notebook.")

    if not metadata:
        st.warning("model_metadata.json not found.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Overview")
        st.markdown(
            f"""
            | Field | Value |
            |---|---|
            | **Algorithm** | {metadata.get('algorithm', 'N/A')} |
            | **Dataset** | {metadata.get('dataset', 'N/A')} |
            | **Author** | {metadata.get('author', 'N/A')} |
            """
        )
    with c2:
        st.markdown("### Performance (validation set)")
        st.metric("R² Score", f"{metrics.get('r2_score', 0):.4f}")
        st.metric("RMSE", f"{metrics.get('rmse', 0):.4f}")
        st.metric("MAE", f"{metrics.get('mae', 0):.4f}")

    st.markdown("### Features (exact notebook order)")
    features = metadata.get("feature_order", metadata.get("features", []))
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
        Streamlit dashboard.

        ### Architecture
        - **Streamlit Cloud:** loads `backend/model.pkl` directly (no separate API server needed).
        - **Local dev (optional):** set `CALORIE_API_URL=http://127.0.0.1:8000` to use FastAPI instead.
        - **Model:** scikit-learn `LinearRegression` on 7 features with R² ≈ 0.968 on the validation split.

        ### Repository
        [ML-Model-Training — Calorie predictions](https://github.com/AreebaBushra/ML-Model-Training/tree/37ec22759908e0eedc83400778e73dec9116012c/Calorie%20predictions_Multivariate%20Linear%20regression)

        ### Run locally
        ```bash
        pip install -r requirements.txt
        streamlit run streamlit_app.py
        ```
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="Calorie Burn Predictor",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()

    metadata = load_metadata()
    metrics = metadata.get("metrics", {})

    pages = {
        "Home": lambda: page_home(metrics),
        "Prediction": page_prediction,
        "History": page_history,
        "Model Information": lambda: page_model_info(metadata, metrics),
        "About": page_about,
    }

    with st.sidebar:
        st.markdown("## 🔥 FitMetrics AI")
        st.caption("Calorie Prediction Dashboard")
        selection = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
        st.markdown("---")
        _, status = is_model_ready()
        st.markdown(f"**Status:** {status}")

    pages[selection]()


if __name__ == "__main__":
    main()
