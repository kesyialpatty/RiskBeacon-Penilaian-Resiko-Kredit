import math

import streamlit as st

try:
    from .DS.feature_engineering import build_display_frame, build_feature_frame
    from .DS.model_utils import predict_risk
except ImportError:
    from DS.feature_engineering import build_display_frame, build_feature_frame
    from DS.model_utils import predict_risk


def render_prediction():
    st.title("Prediction")
    st.write("Enter a customer profile to estimate delinquency risk using `best_lgbm.pkl`.")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=109,
                value=52,
                step=1,
            )
            revolving_utilization_pct = st.number_input(
                "Revolving Utilization",
                min_value=0.0,
                max_value=50708.0,
                value=0.1542,
                step=0.0001,
                format="%.4f",
            )
            debt_ratio = st.number_input(
                "Debt Ratio",
                min_value=0.0,
                max_value=329664.0,
                value=0.3682,
                step=0.0001,
                format="%.4f",
            )
            income = st.number_input(
                "Monthly Income",
                min_value=0.0,
                max_value=3008750.0,
                value=5400.0,
                step=100.0,
                format="%.2f",
            )
            open_loans = st.number_input(
                "Open Credit Lines and Loans",
                min_value=0,
                max_value=58,
                value=8,
                step=1,
            )

        with col2:
            real_estate_loans = st.number_input(
                "Real Estate Loans",
                min_value=0,
                max_value=54,
                value=1,
                step=1,
            )
            dependents = st.number_input(
                "Dependents",
                min_value=0,
                max_value=20,
                value=0,
                step=1,
            )
            late_30_59 = st.number_input(
                "Late 30-59 Days",
                min_value=0,
                max_value=98,
                value=0,
                step=1,
            )
            late_60_89 = st.number_input(
                "Late 60-89 Days",
                min_value=0,
                max_value=98,
                value=0,
                step=1,
            )
            late_90 = st.number_input(
                "Late 90 Days",
                min_value=0,
                max_value=98,
                value=0,
                step=1,
            )

        log_income_preview          = float(math.log1p(income))
        weighted_late_score_preview = late_30_59 * 1 + late_60_89 * 2 + late_90 * 4

        st.markdown("### Auto-generated Features")
        preview_col1, preview_col2 = st.columns(2)
        preview_col1.metric("Log Income",          f"{log_income_preview:.4f}")
        preview_col2.metric("Weighted Late Score", f"{weighted_late_score_preview:.0f}")

        submitted = st.form_submit_button("Estimate Risk")

    if not submitted:
        return

    features = build_feature_frame(
        age=age,
        revolving_utilization_pct=revolving_utilization_pct,
        debt_ratio=debt_ratio,
        income=income,
        open_loans=open_loans,
        real_estate_loans=real_estate_loans,
        dependents=dependents,
        late_30_59=late_30_59,
        late_60_89=late_60_89,
        late_90=late_90,
    )

    result           = predict_risk(features)
    display_features = build_display_frame(features)

    st.subheader("Prediction Result")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Risk Probability",         f"{result['probability']:.2%}")
    metric_col2.metric("Risk Category",            result["label"])
    metric_col3.metric("Recommended Credit Limit", f"${result['recommended_credit_limit']:,.2f}")

    decision_level = "error" if result["recommended_credit_limit"] == 0 else "success"
    if decision_level == "error":
        st.error(result["borrowing_decision"])
    else:
        st.success(result["borrowing_decision"])

    st.caption(f"Prediction source: {result['source']}")

    st.subheader("Feature Frame")
    st.dataframe(display_features, use_container_width=True)
