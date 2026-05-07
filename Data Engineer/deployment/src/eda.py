from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from .gx_validation import DEFAULT_CLEANED_CSV_PATH
except ImportError:
    from gx_validation import DEFAULT_CLEANED_CSV_PATH


TARGET_COLUMN = "target_delinquent"


@st.cache_data
def load_eda_dataframe() -> pd.DataFrame:
    return pd.read_csv(DEFAULT_CLEANED_CSV_PATH)


def _apply_eda_styles() -> None:
    st.markdown(
        """
        <style>
        .eda-source {
            color: #9ca3af;
            font-size: 0.95rem;
            margin-top: -0.5rem;
            margin-bottom: 1rem;
        }
        div[data-baseweb="tab-list"] {
            gap: 1rem;
        }
        button[data-baseweb="tab"] {
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _build_qcut_labels(series: pd.Series, q: int, labels: list[str]) -> pd.Series:
    non_null = series.dropna()
    if non_null.nunique() < 2:
        return pd.Series(pd.NA, index=series.index, dtype="object")

    bucketed_non_null = pd.qcut(non_null, q=min(q, non_null.nunique()), duplicates="drop")
    categories = list(bucketed_non_null.cat.categories)
    label_map = {
        category: labels[index] if index < len(labels) else f"Bucket {index + 1}"
        for index, category in enumerate(categories)
    }

    bucketed_non_null = bucketed_non_null.cat.rename_categories(label_map)
    bucketed = pd.Series(pd.NA, index=series.index, dtype="object")
    bucketed.loc[non_null.index] = bucketed_non_null.astype("object")
    return bucketed


def _bucket_summary(
    dataframe: pd.DataFrame,
    source_column: str,
    bucket_name: str,
    *,
    bins: list[float] | None = None,
    labels: list[str] | None = None,
    qcut: int | None = None,
    order: list[str] | None = None,
) -> pd.DataFrame:
    working = dataframe[[source_column, TARGET_COLUMN]].copy()

    if qcut is not None and labels is not None:
        working[bucket_name] = _build_qcut_labels(working[source_column], qcut, labels)
    else:
        working[bucket_name] = pd.cut(
            working[source_column],
            bins=bins,
            labels=labels,
            include_lowest=True,
        ).astype("object")

    working.loc[working[source_column].isna(), bucket_name] = "Unknown"

    summary = (
        working.groupby(bucket_name, dropna=False)
        .agg(
            default_rate=(TARGET_COLUMN, "mean"),
            customer_count=(TARGET_COLUMN, "size"),
        )
        .reset_index()
    )
    summary["default_rate_pct"] = summary["default_rate"] * 100

    if order:
        available = [value for value in order if value in summary[bucket_name].tolist()]
        remaining = [value for value in summary[bucket_name].tolist() if value not in available]
        summary[bucket_name] = pd.Categorical(summary[bucket_name], categories=available + remaining, ordered=True)
        summary = summary.sort_values(bucket_name)

    return summary


def _delay_bucket_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    working = dataframe[["late_90", TARGET_COLUMN]].copy()
    working["late_90"] = pd.to_numeric(working["late_90"], errors="coerce")
    working["late_90_clean"] = working["late_90"].where(working["late_90"] < 90)
    working["delay_bin"] = pd.cut(
        working["late_90_clean"],
        bins=[-1, 0, 2, 5, 10, np.inf],
        labels=["0", "1-2", "3-5", "6-10", ">10"],
        include_lowest=True,
    ).astype("object")
    working.loc[working["late_90_clean"].isna(), "delay_bin"] = "Unknown"

    summary = (
        working.groupby("delay_bin", dropna=False)
        .agg(
            default_rate=(TARGET_COLUMN, "mean"),
            customer_count=(TARGET_COLUMN, "size"),
        )
        .reset_index()
    )
    summary["default_rate_pct"] = summary["default_rate"] * 100
    summary["delay_bin"] = pd.Categorical(
        summary["delay_bin"],
        categories=["0", "1-2", "3-5", "6-10", ">10", "Unknown"],
        ordered=True,
    )
    return summary.sort_values("delay_bin")


def _render_bucket_chart(
    summary: pd.DataFrame,
    bucket_name: str,
    title: str,
    color: str,
) -> None:
    figure = px.bar(
        summary,
        x=bucket_name,
        y="default_rate_pct",
        color_discrete_sequence=[color],
        text="default_rate_pct",
        custom_data=["customer_count"],
    )
    figure.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Default rate: %{y:.2f}%<br>Customers: %{customdata[0]:,}<extra></extra>",
    )
    figure.update_layout(
        title=title,
        xaxis_title="Segment",
        yaxis_title="Default rate (%)",
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(figure, use_container_width=True)
    st.dataframe(
        summary.rename(
            columns={
                bucket_name: "segment",
                "default_rate_pct": "default_rate_pct",
                "customer_count": "customer_count",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _render_overview(dataframe: pd.DataFrame) -> None:
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{len(dataframe):,}")
    col2.metric("Columns", dataframe.shape[1])
    col3.metric("Default Rate", f"{dataframe[TARGET_COLUMN].mean() * 100:.2f}%")
    col4.metric("Median Income", f"{dataframe['income'].median():,.0f}")

    distribution = (
        dataframe[TARGET_COLUMN]
        .value_counts(dropna=False)
        .rename_axis("target_delinquent")
        .reset_index(name="customer_count")
    )
    distribution["segment"] = distribution["target_delinquent"].map(
        {0: "Non-delinquent", 1: "Delinquent"}
    ).fillna("Unknown")

    figure = px.pie(
        distribution,
        names="segment",
        values="customer_count",
        color="segment",
        color_discrete_map={
            "Non-delinquent": "#22c55e",
            "Delinquent": "#ef4444",
            "Unknown": "#94a3b8",
        },
        hole=0.35,
    )
    figure.update_traces(
        textinfo="percent+label",
        texttemplate="%{label}<br>%{percent}",
        hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Share: %{percent}<extra></extra>",
    )
    figure.update_layout(
        title="Target Distribution",
        legend_title_text="Customer segment",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(figure, use_container_width=True)

def _render_default_pattern(dataframe: pd.DataFrame) -> None:
    st.subheader("Default Pattern Analysis")
    summary = _delay_bucket_summary(dataframe)
    _render_bucket_chart(summary, "delay_bin", "Default Rate by 90-Day Delinquency History", "#ef4444")

    highest = summary.loc[summary["default_rate_pct"].idxmax()]
    no_delay = summary.loc[summary["delay_bin"] == "0"].iloc[0]
    frequent_delay = summary.loc[summary["delay_bin"] == "6-10"].iloc[0]
    severe_delay = summary.loc[summary["delay_bin"] == ">10"].iloc[0]
    unknown_delay = summary.loc[summary["delay_bin"] == "Unknown"].iloc[0]
    st.caption(
        f"The riskiest segment is `{highest['delay_bin']}` with a default rate of "
        f"{highest['default_rate_pct']:.2f}% across {int(highest['customer_count']):,} borrowers."
    )
    st.markdown(
        f"""
        **Insight**

        Ninety-day delinquency history is a very strong default predictor. When borrowers have no delay (`0`),
        the default rate stays near `{no_delay['default_rate_pct']:.2f}%` across a very large base of
        `{int(no_delay['customer_count']):,}` borrowers. Once delays begin to repeat, the risk rises sharply:
        the `1-2` bucket is already at `{summary.loc[summary['delay_bin'] == '1-2', 'default_rate_pct'].iloc[0]:.2f}%`,
        the `3-5` bucket reaches `{summary.loc[summary['delay_bin'] == '3-5', 'default_rate_pct'].iloc[0]:.2f}%`,
        and the `6-10` bucket peaks at `{frequent_delay['default_rate_pct']:.2f}%`.

        The more extreme `>10` bucket still remains elevated at `{severe_delay['default_rate_pct']:.2f}%`,
        but it should be interpreted carefully because the sample is much smaller. That pattern may reflect
        limited observations or operational intervention such as restructuring, collections, or other bank actions.
        The `Unknown` bucket also matters because it records a `{unknown_delay['default_rate_pct']:.2f}%` default rate
        across `{int(unknown_delay['customer_count']):,}` records, making it safer to preserve as a risk signal
        instead of forcing it to zero or a median value. The business takeaway remains clear:
        heavier delinquency history is strongly associated with a higher likelihood of default.
        """
    )


def _render_payment_behavior(dataframe: pd.DataFrame) -> None:
    st.subheader("Payment Behavior")
    summary = _bucket_summary(
        dataframe,
        "revolving_utilization_pct",
        "utilization_bin",
        qcut=5,
        labels=["Very Low", "Low", "Medium", "High", "Very High"],
        order=["Very Low", "Low", "Medium", "High", "Very High", "Unknown"],
    )
    _render_bucket_chart(summary, "utilization_bin", "Default Rate by Revolving Utilization", "#f97316")

    highest = summary.loc[summary["default_rate_pct"].idxmax()]
    st.caption(
        f"The highest utilization segment is `{highest['utilization_bin']}` "
        f"with a default rate of {highest['default_rate_pct']:.2f}%."
    )


def _render_financial_capacity(dataframe: pd.DataFrame) -> None:
    st.subheader("Financial Capacity")
    summary = _bucket_summary(
        dataframe,
        "income",
        "income_bin",
        qcut=4,
        labels=["Low", "Medium", "High", "Very High"],
        order=["Low", "Medium", "High", "Very High", "Unknown"],
    )
    _render_bucket_chart(summary, "income_bin", "Default Rate by Monthly Income", "#3b82f6")

    heatmap_source = dataframe[["income", "debt_ratio", TARGET_COLUMN]].copy()
    heatmap_source["income_band"] = _build_qcut_labels(
        heatmap_source["income"], 4, ["Low", "Medium", "High", "Very High"]
    )
    heatmap_source["debt_band"] = pd.cut(
        heatmap_source["debt_ratio"],
        bins=[-0.01, 0.25, 0.5, 0.75, 1.0, np.inf],
        labels=["0-0.25", "0.25-0.50", "0.50-0.75", "0.75-1.00", ">1.00"],
        include_lowest=True,
    ).astype("object")
    heatmap_source.loc[heatmap_source["income"].isna(), "income_band"] = "Unknown"
    heatmap_source.loc[heatmap_source["debt_ratio"].isna(), "debt_band"] = "Unknown"

    heatmap = (
        heatmap_source.groupby(["income_band", "debt_band"], dropna=False)[TARGET_COLUMN]
        .mean()
        .mul(100)
        .reset_index(name="default_rate_pct")
    )

    figure = px.density_heatmap(
        heatmap,
        x="income_band",
        y="debt_band",
        z="default_rate_pct",
        color_continuous_scale="Reds",
        text_auto=".1f",
    )
    figure.update_layout(
        title="Debt Ratio vs Income Band",
        xaxis_title="Income band",
        yaxis_title="Debt ratio band",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(figure, use_container_width=True)


def _render_credit_exposure(dataframe: pd.DataFrame) -> None:
    st.subheader("Credit Exposure")
    summary = _bucket_summary(
        dataframe,
        "open_loans",
        "loan_bin",
        bins=[-1, 2, 5, 10, 20, np.inf],
        labels=["Very Low", "Low", "Medium", "High", "Very High"],
        order=["Very Low", "Low", "Medium", "High", "Very High", "Unknown"],
    )
    _render_bucket_chart(summary, "loan_bin", "Default Rate by Number of Open Loans", "#8b5cf6")
    very_low = summary.loc[summary["loan_bin"] == "Very Low"].iloc[0]
    medium = summary.loc[summary["loan_bin"] == "Medium"].iloc[0]
    very_high = summary.loc[summary["loan_bin"] == "Very High"].iloc[0]
    st.markdown(
        f"""
        **Insight**

        The number of open accounts shows a meaningful pattern: too few accounts can itself be a risk signal.
        In the `Very Low` bucket, the default rate is `{very_low['default_rate_pct']:.2f}%` across
        `{int(very_low['customer_count']):,}` borrowers. This may indicate thin credit history, newer borrowers,
        or customers without a stable repayment track record. By contrast, the `Medium` bucket looks like the
        healthiest zone, with a `{medium['default_rate_pct']:.2f}%` default rate and the largest sample size,
        `{int(medium['customer_count']):,}` borrowers, making it the strongest candidate for a relative safe zone.

        Once account counts become too high, risk starts to rise again. The `Very High` bucket moves up to
        `{very_high['default_rate_pct']:.2f}%`, which suggests that excessive credit exposure should still be monitored
        because it can reflect more complex debt obligations and a narrower repayment cushion.
        """
    )


def _render_customer_profile(dataframe: pd.DataFrame) -> None:
    st.subheader("Customer Profile")
    age_summary = _bucket_summary(
        dataframe,
        "age",
        "age_bin",
        bins=[0, 30, 45, 60, 120],
        labels=["<30", "30-45", "45-60", ">60"],
        order=["<30", "30-45", "45-60", ">60", "Unknown"],
    )
    _render_bucket_chart(age_summary, "age_bin", "Default Rate by Age Group", "#0f766e")

    summary = _bucket_summary(
        dataframe,
        "dependents",
        "dependents_bin",
        bins=[-1, 0, 2, 5, 10, np.inf],
        labels=["0", "1-2", "3-5", "6-10", ">10"],
        order=["0", "1-2", "3-5", "6-10", ">10", "Unknown"],
    )
    _render_bucket_chart(summary, "dependents_bin", "Default Rate by Number of Dependents", "#14b8a6")


def _render_risk_dashboard(dataframe: pd.DataFrame) -> None:
    st.subheader("Customer Credit Risk Dashboard")

    age_summary = _bucket_summary(
        dataframe,
        "age",
        "age_bin",
        bins=[0, 30, 45, 60, 120],
        labels=["<30", "30-45", "45-60", ">60"],
        order=["<30", "30-45", "45-60", ">60", "Unknown"],
    )
    income_summary = _bucket_summary(
        dataframe,
        "income",
        "income_bin",
        qcut=4,
        labels=["Low", "Medium", "High", "Very High"],
        order=["Low", "Medium", "High", "Very High", "Unknown"],
    )
    dependents_exact = (
        dataframe[["dependents", TARGET_COLUMN]]
        .dropna()
        .assign(dependents=lambda frame: pd.to_numeric(frame["dependents"], errors="coerce"))
        .dropna()
    )
    dependents_exact = dependents_exact.loc[dependents_exact["dependents"] <= 10]
    dependents_summary = (
        dependents_exact.groupby("dependents")[TARGET_COLUMN]
        .agg(default_rate="mean", customer_count="size")
        .reset_index()
    )
    dependents_summary["default_rate_pct"] = dependents_summary["default_rate"] * 100
    dependents_summary["dependents"] = dependents_summary["dependents"].astype(int).astype(str)

    util_summary = _bucket_summary(
        dataframe,
        "revolving_utilization_pct",
        "util_bin",
        qcut=5,
        labels=["Very Low", "Low", "Medium", "High", "Very High"],
        order=["Very Low", "Low", "Medium", "High", "Very High", "Unknown"],
    )
    delay_summary = _delay_bucket_summary(dataframe)

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    row3_col1, row3_col2 = st.columns(2)

    with row1_col1:
        _render_bucket_chart(age_summary, "age_bin", "Default Rate by Age Group", "#10b981")

    with row1_col2:
        _render_bucket_chart(income_summary, "income_bin", "Default Rate by Income Group", "#3b82f6")

    with row2_col1:
        figure = px.bar(
            dependents_summary,
            x="dependents",
            y="default_rate_pct",
            color_discrete_sequence=["#ec4899"],
            text="default_rate_pct",
            custom_data=["customer_count"],
        )
        figure.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            hovertemplate="<b>%{x} dependents</b><br>Default rate: %{y:.2f}%<br>Customers: %{customdata[0]:,}<extra></extra>",
        )
        figure.update_layout(
            title="Default Rate by Exact Number of Dependents",
            xaxis_title="Dependents",
            yaxis_title="Default rate (%)",
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(figure, use_container_width=True)

    with row2_col2:
        _render_bucket_chart(util_summary, "util_bin", "Default Rate by Utilization", "#f97316")

    with row3_col1:
        _render_bucket_chart(delay_summary, "delay_bin", "Default Rate by Delay Frequency", "#ef4444")

    with row3_col2:
        st.markdown(
            """
            ### Key Insights
            1. Younger clients, especially `<30`, show materially higher risk.
            2. Past-due history remains the strongest predictor of default.
            3. Financial burden from additional dependents is consistently visible.
            4. High utilization indicates cash-flow stress and elevated delinquency risk.
            5. Income segmentation helps separate resilient and vulnerable customer groups.
            """
        )


def render_eda() -> None:
    _apply_eda_styles()

    st.title("Exploratory Data Analysis")
    st.markdown(
        "<div class='eda-source'>EDA view for the cleaned Hugging Face dataset.</div>",
        unsafe_allow_html=True,
    )

    if not DEFAULT_CLEANED_CSV_PATH.exists():
        st.error(f"Cleaned CSV not found: {DEFAULT_CLEANED_CSV_PATH}")
        return

    dataframe = load_eda_dataframe()

    overview_tab, default_tab, payment_tab, financial_tab, exposure_tab, profile_tab, dashboard_tab = st.tabs(
        [
            "Overview",
            "Default Pattern",
            "Payment Behavior",
            "Financial Capacity",
            "Credit Exposure",
            "Customer Profile",
            "Risk Dashboard",
        ]
    )

    with overview_tab:
        _render_overview(dataframe)

    with default_tab:
        _render_default_pattern(dataframe)

    with payment_tab:
        _render_payment_behavior(dataframe)

    with financial_tab:
        _render_financial_capacity(dataframe)

    with exposure_tab:
        _render_credit_exposure(dataframe)

    with profile_tab:
        _render_customer_profile(dataframe)

    with dashboard_tab:
        _render_risk_dashboard(dataframe)
