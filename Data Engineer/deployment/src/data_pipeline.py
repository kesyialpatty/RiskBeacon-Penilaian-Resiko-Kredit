import json
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from .gx_validation import (
        BUSINESS_COLUMNS,
        DEFAULT_CLEANED_CSV_PATH,
        GX_RESULTS_PATH,
        validate_default_cleaned_csv_with_gx,
    )
except ImportError:
    from gx_validation import (
        BUSINESS_COLUMNS,
        DEFAULT_CLEANED_CSV_PATH,
        GX_RESULTS_PATH,
        validate_default_cleaned_csv_with_gx,
    )


GX_RULE_LABELS = {
    ("expect_column_values_to_be_in_set", "target_delinquent"): "Target delinquent must be 0 or 1.",
    ("expect_column_values_to_be_between", "age"): "Age must be greater than or equal to 21.",
    ("expect_column_values_to_be_between", "dependents"): "Dependents cannot be greater than 10.",
    ("expect_column_values_to_be_between", "open_loans"): "Open loans cannot be greater than 30.",
    (
        "expect_column_pair_values_A_to_be_greater_than_B",
        "max_lifetime_days",
    ): "Age must be logically consistent with delinquency history.",
}

RAW_SOURCE_COLUMNS = [
    "SeriousDlqin2yrs",
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfTime30-59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60-89DaysPastDueNotWorse",
    "NumberOfDependents",
]


@st.cache_data
def load_cleaned_dataframe():
    return pd.read_csv(DEFAULT_CLEANED_CSV_PATH)


def _label_age(value):
    if pd.isna(value):
        return "unknown"
    if value < 30:
        return "under_30"
    if value <= 45:
        return "30_to_45"
    if value <= 60:
        return "46_to_60"
    return "above_60"


def _label_income(value):
    if pd.isna(value):
        return "unknown"
    if value < 3000:
        return "low"
    if value < 8000:
        return "medium"
    if value < 15000:
        return "high"
    return "very_high"


def _label_dependents(value):
    if pd.isna(value):
        return "unknown"
    if value <= 0:
        return "0"
    if value <= 2:
        return "1_to_2"
    return "3_plus"


def _label_revolving_utilization(value):
    if pd.isna(value):
        return "unknown"
    if value < 0.3:
        return "low"
    if value < 0.7:
        return "medium"
    if value <= 1.0:
        return "high"
    return "very_high"


def _label_open_loans(value):
    if pd.isna(value):
        return "unknown"
    if value <= 5:
        return "0_to_5"
    if value <= 10:
        return "6_to_10"
    if value <= 20:
        return "11_to_20"
    return "21_plus"


def _label_real_estate_loans(value):
    if pd.isna(value):
        return "unknown"
    if value <= 0:
        return "0"
    if value == 1:
        return "1"
    return "2_plus"


def _label_late_count(value):
    if pd.isna(value):
        return "unknown"
    if value <= 0:
        return "0"
    if value <= 2:
        return "1_to_2"
    return "3_plus"


@st.cache_data
def build_datamart_overview(dataframe):
    datamart = dataframe.copy()
    datamart["age_group"] = pd.to_numeric(datamart["age"], errors="coerce").apply(_label_age)
    datamart["income_band"] = pd.to_numeric(datamart["income"], errors="coerce").apply(_label_income)
    datamart["dependents_band"] = pd.to_numeric(datamart["dependents"], errors="coerce").apply(_label_dependents)
    datamart["revolving_utilization_band"] = pd.to_numeric(
        datamart["revolving_utilization_pct"], errors="coerce"
    ).apply(_label_revolving_utilization)
    datamart["open_loans_band"] = pd.to_numeric(datamart["open_loans"], errors="coerce").apply(_label_open_loans)
    datamart["real_estate_loans_band"] = pd.to_numeric(
        datamart["real_estate_loans"], errors="coerce"
    ).apply(_label_real_estate_loans)
    datamart["late_30_59_band"] = pd.to_numeric(datamart["late_30_59"], errors="coerce").apply(_label_late_count)
    datamart["late_60_89_band"] = pd.to_numeric(datamart["late_60_89"], errors="coerce").apply(_label_late_count)
    datamart["late_90_band"] = pd.to_numeric(datamart["late_90"], errors="coerce").apply(_label_late_count)

    customer_dimension_columns = ["age_group", "income_band", "dependents_band"]
    credit_dimension_columns = [
        "revolving_utilization_band",
        "open_loans_band",
        "real_estate_loans_band",
    ]
    delinquency_dimension_columns = ["late_30_59_band", "late_60_89_band", "late_90_band"]

    table_summary = pd.DataFrame(
        [
            {
                "table_name": "dim_customer_segment",
                "table_type": "dimension",
                "row_count": len(datamart[customer_dimension_columns].drop_duplicates()),
                "column_count": len(customer_dimension_columns),
                "grain": "one row per age, income, and dependents segment",
            },
            {
                "table_name": "dim_credit_profile",
                "table_type": "dimension",
                "row_count": len(datamart[credit_dimension_columns].drop_duplicates()),
                "column_count": len(credit_dimension_columns),
                "grain": "one row per utilization, open loans, and real estate profile",
            },
            {
                "table_name": "dim_delinquency_profile",
                "table_type": "dimension",
                "row_count": len(datamart[delinquency_dimension_columns].drop_duplicates()),
                "column_count": len(delinquency_dimension_columns),
                "grain": "one row per delinquency frequency combination",
            },
            {
                "table_name": "fact_credit_risk",
                "table_type": "fact",
                "row_count": len(datamart),
                "column_count": 10,
                "grain": "one row per cleaned customer credit record",
            },
        ]
    )

    dimension_details = pd.DataFrame(
        [
            {"table_name": "dim_customer_segment", "columns": ", ".join(customer_dimension_columns)},
            {"table_name": "dim_credit_profile", "columns": ", ".join(credit_dimension_columns)},
            {"table_name": "dim_delinquency_profile", "columns": ", ".join(delinquency_dimension_columns)},
            {
                "table_name": "fact_credit_risk",
                "columns": ", ".join(
                    [
                        "customer_segment_key",
                        "credit_profile_key",
                        "delinquency_profile_key",
                        "source_record_hash",
                        "target_delinquent",
                        "income",
                        "log_income",
                        "debt_ratio",
                        "weighted_late_score",
                        "record_count",
                    ]
                ),
            },
        ]
    )

    return table_summary, dimension_details


def _apply_pipeline_styles():
    st.markdown(
        """
        <style>
        .pipeline-source {
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


def _load_validation_result():
    try:
        validation_payload = validate_default_cleaned_csv_with_gx()
        return validation_payload["validation_result"], validation_payload["results_path"], None
    except ModuleNotFoundError:
        if GX_RESULTS_PATH.exists():
            cached_result = json.loads(GX_RESULTS_PATH.read_text(encoding="utf-8"))
            return cached_result, str(GX_RESULTS_PATH), "Showing cached GX result because Great Expectations is not installed in this environment."
        return None, None, "Great Expectations is not installed in this environment yet."
    except Exception as exc:
        if GX_RESULTS_PATH.exists():
            cached_result = json.loads(GX_RESULTS_PATH.read_text(encoding="utf-8"))
            return cached_result, str(GX_RESULTS_PATH), f"Using cached GX result because live validation failed: {exc}"
        return None, None, str(exc)


def _summarize_validation_result(validation_result):
    summarized_results = []
    for item in validation_result.get("results", []):
        expectation_type = item.get("expectation_config", {}).get("expectation_type")
        kwargs = item.get("expectation_config", {}).get("kwargs", {})
        result = item.get("result", {})
        column_name = kwargs.get("column", kwargs.get("column_A", "-"))

        if expectation_type == "expect_column_values_to_not_be_null":
            description = f"Column `{column_name}` must not contain missing values."
        else:
            description = GX_RULE_LABELS.get((expectation_type, column_name), expectation_type)

        summarized_results.append(
            {
                "rule": description,
                "expectation": expectation_type,
                "column": column_name,
                "status": "Passed" if item.get("success") else "Failed",
                "unexpected_count": result.get("unexpected_count", 0),
                "unexpected_percent": round(result.get("unexpected_percent", 0.0), 4),
            }
        )

    return pd.DataFrame(summarized_results)


def _render_raw_overview(dataframe):
    st.subheader("Raw Source Overview")

    raw_overview = pd.DataFrame(
        [
            {
                "dataset_name": "cs-training.csv",
                "stage": "raw source",
                "row_count": "150,000",
                "column_count": len(RAW_SOURCE_COLUMNS),
                "description": "Original borrower-level credit dataset before renaming, anomaly handling, and validation.",
            }
        ]
    )
    st.dataframe(raw_overview, use_container_width=True, hide_index=True)

    raw_schema = pd.DataFrame(
        [
            {"column_name": "SeriousDlqin2yrs", "business_meaning": "default target"},
            {
                "column_name": "RevolvingUtilizationOfUnsecuredLines",
                "business_meaning": "credit utilization ratio",
            },
            {"column_name": "age", "business_meaning": "borrower age"},
            {
                "column_name": "NumberOfTime30-59DaysPastDueNotWorse",
                "business_meaning": "30-59 day delinquency count",
            },
            {"column_name": "DebtRatio", "business_meaning": "debt burden ratio"},
            {"column_name": "MonthlyIncome", "business_meaning": "monthly borrower income"},
            {
                "column_name": "NumberOfOpenCreditLinesAndLoans",
                "business_meaning": "number of open loans",
            },
            {"column_name": "NumberOfTimes90DaysLate", "business_meaning": "90-day delinquency count"},
            {
                "column_name": "NumberRealEstateLoansOrLines",
                "business_meaning": "real estate loan count",
            },
            {
                "column_name": "NumberOfTime60-89DaysPastDueNotWorse",
                "business_meaning": "60-89 day delinquency count",
            },
            {"column_name": "NumberOfDependents", "business_meaning": "household dependents"},
        ]
    )
    st.markdown("### Raw Source Columns")
    st.dataframe(raw_schema, use_container_width=True, hide_index=True)

    st.markdown("### Cleaned Dataset and Datamart")
    cleaned_summary = pd.DataFrame(
        [
            {
                "dataset_name": "cleaned_cs_training.csv",
                "stage": "cleaned dataset",
                "row_count": f"{len(dataframe):,}",
                "column_count": dataframe.shape[1],
                "description": "Snake_case modeling dataset after duplicate removal, cleaning rules, and feature derivation.",
            }
        ]
    )
    st.dataframe(cleaned_summary, use_container_width=True, hide_index=True)

    table_summary, dimension_details = build_datamart_overview(dataframe)
    st.markdown("### Datamart Fact and Dimension Overview")
    st.dataframe(table_summary, use_container_width=True, hide_index=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fact Rows", f"{int(table_summary.loc[table_summary['table_name'] == 'fact_credit_risk', 'row_count'].iloc[0]):,}")
    col2.metric("Customer Segments", f"{int(table_summary.loc[table_summary['table_name'] == 'dim_customer_segment', 'row_count'].iloc[0]):,}")
    col3.metric("Credit Profiles", f"{int(table_summary.loc[table_summary['table_name'] == 'dim_credit_profile', 'row_count'].iloc[0]):,}")
    col4.metric(
        "Delinquency Profiles",
        f"{int(table_summary.loc[table_summary['table_name'] == 'dim_delinquency_profile', 'row_count'].iloc[0]):,}",
    )

    st.markdown("### Table Columns")
    st.dataframe(dimension_details, use_container_width=True, hide_index=True)


def _render_missing_monitor(dataframe):
    st.subheader("Missing Value Monitoring")

    missing_summary = (
        dataframe[BUSINESS_COLUMNS]
        .isnull()
        .mean()
        .mul(100)
        .reset_index()
        .rename(columns={"index": "column", 0: "missing_rate"})
        .sort_values("missing_rate", ascending=False)
    )
    missing_summary["status"] = missing_summary["missing_rate"].apply(
        lambda value: "Failed" if value > 0 else "Passed"
    )

    if (missing_summary["missing_rate"] > 0).any():
        st.warning("Some business columns still contain missing values.")
    else:
        st.success("All business columns are complete with no missing values.")

    st.dataframe(missing_summary, use_container_width=True)
    st.bar_chart(missing_summary.set_index("column")["missing_rate"])


def _render_diagnostics(dataframe, validation_result, results_path, validation_note):
    st.subheader("GX Validation Summary")

    if validation_note:
        st.info(validation_note)

    if validation_result is None:
        st.error("GX validation result is not available.")
        return

    statistics = validation_result.get("statistics", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Validation Suite", validation_result.get("meta", {}).get("expectation_suite_name", "default"))
    col2.metric(
        "Checks Passed",
        f"{statistics.get('successful_expectations', 0)}/{statistics.get('evaluated_expectations', 0)}",
    )
    col3.metric("Success Rate", f"{statistics.get('success_percent', 0.0):.2f}%")

    if validation_result.get("success"):
        st.success("GX runtime validation passed.")
    else:
        st.warning("GX runtime validation found issues that need review.")

    st.caption(f"Validation source: `{results_path}`")
    st.dataframe(_summarize_validation_result(validation_result), use_container_width=True)

    diagnostics = pd.DataFrame(
        [
            {
                "rule": "age < 21",
                "failed_rows": int((pd.to_numeric(dataframe["age"], errors="coerce") < 21).fillna(False).sum()),
            },
            {
                "rule": "target_delinquent not in {0,1}",
                "failed_rows": int((~dataframe["target_delinquent"].isin([0, 1])).fillna(False).sum()),
            },
            {
                "rule": "dependents > 10",
                "failed_rows": int((pd.to_numeric(dataframe["dependents"], errors="coerce") > 10).fillna(False).sum()),
            },
            {
                "rule": "open_loans > 30",
                "failed_rows": int((pd.to_numeric(dataframe["open_loans"], errors="coerce") > 30).fillna(False).sum()),
            },
            {
                "rule": "late history exceeds lifetime days",
                "failed_rows": int(
                    (
                        (pd.to_numeric(dataframe["age"], errors="coerce") * 365)
                        < (
                            pd.to_numeric(dataframe["late_30_59"], errors="coerce") * 30
                            + pd.to_numeric(dataframe["late_60_89"], errors="coerce") * 60
                            + pd.to_numeric(dataframe["late_90"], errors="coerce") * 90
                        )
                    ).fillna(False).sum()
                ),
            },
        ]
    )

    st.markdown("### Business Rule Diagnostics")
    st.dataframe(diagnostics, use_container_width=True)


def _render_pipeline_construction():
    st.subheader("Pipeline Construction")

    pipeline_steps = pd.DataFrame(
        [
            {
                "step": 1,
                "stage": "Extract",
                "input": "credit scoring source data",
                "output": "raw training dataset",
                "description": "Load source records into the project pipeline.",
            },
            {
                "step": 2,
                "stage": "Transform",
                "input": "raw training dataset",
                "output": "cleaned snake_case dataset",
                "description": "Rename columns, coerce numeric fields, remove duplicates, and standardize the modeling base table.",
            },
            {
                "step": 3,
                "stage": "Feature Engineering",
                "input": "cleaned base dataset",
                "output": "derived analytical fields",
                "description": "Generate `log_income` and `weighted_late_score` for analytics and inference.",
            },
            {
                "step": 4,
                "stage": "Validation",
                "input": "cleaned dataset",
                "output": "GX validation result",
                "description": "Check business rules, null completeness, and logical consistency before downstream use.",
            },
            {
                "step": 5,
                "stage": "Datamart Modeling",
                "input": "cleaned dataset",
                "output": "fact and dimension tables",
                "description": "Build `dim_customer_segment`, `dim_credit_profile`, `dim_delinquency_profile`, and `fact_credit_risk`.",
            },
            {
                "step": 6,
                "stage": "Serving",
                "input": "validated features and model artifacts",
                "output": "prediction-ready app",
                "description": "Expose the validated schema to the Streamlit prediction workflow.",
            },
        ]
    )
    st.dataframe(pipeline_steps, use_container_width=True, hide_index=True)

    schema_path = Path(__file__).resolve().parent / "DS" / "model_schema.json"
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_rows = []
        target_column = schema.get("target_column")
        if target_column:
            schema_rows.append({"column_name": target_column, "column_role": "target"})
        for column_name in schema.get("feature_columns", []):
            schema_rows.append(
                {
                    "column_name": column_name,
                    "column_role": "derived feature" if column_name in schema.get("derived_columns", []) else "input feature",
                }
            )

        st.markdown("### Inference Schema")
        st.dataframe(pd.DataFrame(schema_rows), use_container_width=True, hide_index=True)

def render_data_pipeline():
    _apply_pipeline_styles()

    st.title("Data Pipeline & Quality Overview")
    st.markdown(
        f"<div class='pipeline-source'>Cleaned CSV source: {DEFAULT_CLEANED_CSV_PATH}</div>",
        unsafe_allow_html=True,
    )

    if not DEFAULT_CLEANED_CSV_PATH.exists():
        st.error(f"Cleaned CSV not found: {DEFAULT_CLEANED_CSV_PATH}")
        return

    dataframe = load_cleaned_dataframe()
    validation_result, results_path, validation_note = _load_validation_result()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Raw Overview", "Missing Monitor", "Diagnostics", "Pipeline Construction"]
    )

    with tab1:
        _render_raw_overview(dataframe)

    with tab2:
        _render_missing_monitor(dataframe)

    with tab3:
        _render_diagnostics(dataframe, validation_result, results_path, validation_note)

    with tab4:
        _render_pipeline_construction()
