from __future__ import annotations

from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "riskbeacon_v2_bold_red.png"


def _apply_home_styles() -> None:
    st.markdown(
        """
        <style>
        .home-shell {
            background: linear-gradient(180deg, #160607 0%, #0f1117 22%, #0f1117 100%);
            border: 1px solid rgba(220, 38, 38, 0.14);
            border-radius: 28px;
            padding: 1.8rem 1.4rem 1.6rem;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.22);
        }
        .home-section-title {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 800;
            margin: 0 0 0.9rem 0;
        }
        .home-copy {
            color: #f3f4f6;
            font-size: 1.02rem;
            line-height: 1.8;
            margin-bottom: 1rem;
        }
        .home-copy strong {
            color: #ffffff;
        }
        .home-list {
            color: #f3f4f6;
            font-size: 1rem;
            line-height: 1.8;
            padding-left: 1.1rem;
            margin: 0 0 1rem 0;
        }
        .component-list {
            color: #f3f4f6;
            font-size: 1rem;
            line-height: 1.8;
            padding-left: 1.15rem;
            margin-top: 0.2rem;
        }
        .component-list li {
            margin-bottom: 1rem;
        }
        .component-list strong {
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home() -> None:
    _apply_home_styles()

    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if LOGO_PATH.exists():
        left_spacer, center_logo, right_spacer = st.columns([1, 2, 1])
        with center_logo:
            st.image(str(LOGO_PATH), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='home-shell'>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown("<div class='home-section-title'>About Us</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="home-copy">
            RiskBeacon is a <strong>credit risk scoring system</strong> designed to assess and monitor the probability of borrower default before credit decisions are made.
            </div>
            <div class="home-copy">
            As financial institutions, from banks to cooperative lenders, continue to expand their reach, subjective credit assessment remains a critical operational risk. Over-reliance on social reputation and informal judgment can lead to:
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <ul class="home-list">
                <li>Increased non-performing loans (NPL)</li>
                <li>Inconsistent and biased credit decisions</li>
                <li>Financial losses from preventable defaults, especially in communities where <strong>character assessment lacks data foundation</strong></li>
            </ul>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="home-copy">
            RiskBeacon transforms historical borrower data into <strong>objective, data-driven credit decisions</strong> through an integrated analysis and modeling pipeline grounded in the universally recognized <strong>5C of Credit</strong> principles: Character, Capacity, Capital, Collateral, and Conditions.
            </div>
            <div class="home-copy">
            The system is built to serve both <strong>banking institutions</strong> and <strong>savings and loan cooperatives</strong>, bridging the gap between informal trust-based lending and modern predictive analytics.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown("<div class='home-section-title'>System Components</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <ul class="component-list">
                <li><strong>Data Pipeline &amp; Quality Monitoring</strong><br>Structured ingestion, transformation, and validation of historical borrower data, handling missing values, outliers, and class imbalance to ensure model-ready data quality.</li>
                <li><strong>Exploratory Data Analysis</strong><br>Business insights into borrower behavior mapped across the 5C framework, identifying which financial and behavioral patterns most strongly predict default risk.</li>
                <li><strong>Predictive Modeling</strong><br>A gradient boosting classification model (LightGBM) trained to estimate the probability of default (PD) at the individual borrower level, evaluated using ROC-AUC, Recall, and KS-Statistic.</li>
                <li><strong>Model Explainability</strong><br>SHAP-based feature attribution to explain why each borrower receives their risk score, supporting transparency, regulatory compliance, and trust from credit officers.</li>
                <li><strong>Operational Risk Monitoring</strong><br>Risk segmentation into Low, Medium, and High tiers based on PD score distribution, enabling proactive intervention and consistent, data-backed credit approval decisions.</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
