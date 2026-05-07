import json
from pathlib import Path

import pandas as pd


GX_RESULTS_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "gx" / "last_validation.json"
DEFAULT_CLEANED_CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "cleaned_cs_training.csv"

BUSINESS_COLUMNS = [
    "target_delinquent",
    "revolving_utilization_pct",
    "age",
    "late_30_59",
    "debt_ratio",
    "income",
    "open_loans",
    "late_90",
    "real_estate_loans",
    "late_60_89",
    "dependents",
    "log_income",
    "weighted_late_score",
]


def _format_failed_expectations(validation_result):
    failed = []
    for item in validation_result.get("results", []):
        if item.get("success"):
            continue

        expectation_type = item.get("expectation_config", {}).get("expectation_type")
        kwargs = item.get("expectation_config", {}).get("kwargs", {})
        failed.append({"expectation": expectation_type, "kwargs": kwargs})
    return failed


def _prepare_dataframe(dataframe):
    prepared = dataframe.copy()

    numeric_columns = [
        "target_delinquent",
        "revolving_utilization_pct",
        "age",
        "late_30_59",
        "debt_ratio",
        "income",
        "open_loans",
        "late_90",
        "real_estate_loans",
        "late_60_89",
        "dependents",
        "log_income",
        "weighted_late_score",
    ]
    for column_name in numeric_columns:
        if column_name in prepared.columns:
            prepared[column_name] = pd.to_numeric(prepared[column_name], errors="coerce")

    required_for_derived = {"age", "late_30_59", "late_60_89", "late_90"}
    if required_for_derived.issubset(prepared.columns):
        prepared["late_history_days"] = (
            prepared["late_30_59"] * 30
            + prepared["late_60_89"] * 60
            + prepared["late_90"] * 90
        )
        prepared["max_lifetime_days"] = prepared["age"] * 365

    return prepared


def validate_dataframe_with_gx(dataframe):
    import great_expectations as ge

    prepared = _prepare_dataframe(dataframe)
    validator = ge.from_pandas(prepared)

    validator.expect_column_values_to_be_in_set("target_delinquent", [0, 1])
    validator.expect_column_values_to_be_between("age", min_value=21)
    validator.expect_column_values_to_be_between("dependents", min_value=0, max_value=10)
    validator.expect_column_values_to_be_between("open_loans", min_value=0, max_value=30)

    for column_name in BUSINESS_COLUMNS:
        validator.expect_column_values_to_not_be_null(column_name)

    validator.expect_column_pair_values_A_to_be_greater_than_B(
        "max_lifetime_days",
        "late_history_days",
        or_equal=True,
    )

    validation_result = validator.validate(result_format="SUMMARY").to_json_dict()

    GX_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    GX_RESULTS_PATH.write_text(json.dumps(validation_result, indent=2), encoding="utf-8")

    return {
        "success": validation_result.get("success", False),
        "statistics": validation_result.get("statistics", {}),
        "failed_expectations": _format_failed_expectations(validation_result),
        "validation_result": validation_result,
        "results_path": str(GX_RESULTS_PATH),
    }


def validate_csv_with_gx(file_or_path):
    dataframe = pd.read_csv(file_or_path)
    return validate_dataframe_with_gx(dataframe)


def validate_default_cleaned_csv_with_gx():
    if not DEFAULT_CLEANED_CSV_PATH.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {DEFAULT_CLEANED_CSV_PATH}")

    return validate_csv_with_gx(DEFAULT_CLEANED_CSV_PATH)
