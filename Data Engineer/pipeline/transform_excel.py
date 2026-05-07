from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_EXCEL_PATH = PROJECT_ROOT / "data" / "raw_cs_training.xlsx"
DEFAULT_CLEANED_EXCEL_PATH = PROJECT_ROOT / "data" / "cleaned_cs_training.xlsx"

COLUMN_RENAME_MAP = {
    "SeriousDlqin2yrs": "target_delinquent",
    "NumberOfTime30-59DaysPastDueNotWorse": "late_30_59",
    "NumberOfTime60-89DaysPastDueNotWorse": "late_60_89",
    "NumberOfTimes90DaysLate": "late_90",
    "RevolvingUtilizationOfUnsecuredLines": "revolving_utilization_pct",
    "NumberOfOpenCreditLinesAndLoans": "open_loans",
    "NumberRealEstateLoansOrLines": "real_estate_loans",
    "NumberOfDependents": "dependents",
    "MonthlyIncome": "income",
}


def normalize_column_name(name: str, position: int, seen: set[str]) -> str:
    raw_name = "" if name is None else str(name).strip()

    if not raw_name or raw_name.lower().startswith("unnamed"):
        normalized = f"column_{position}"
    elif raw_name in COLUMN_RENAME_MAP:
        normalized = COLUMN_RENAME_MAP[raw_name]
    else:
        normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", raw_name)
        normalized = re.sub(r"[^0-9A-Za-z]+", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_").lower()
        normalized = normalized or f"column_{position}"

    base_name = normalized
    suffix = 1
    while normalized in seen:
        suffix += 1
        normalized = f"{base_name}_{suffix}"

    seen.add(normalized)
    return normalized


def add_engineered_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = ["income", "late_30_59", "late_60_89", "late_90"]
    for column_name in numeric_columns:
        if column_name in dataframe.columns:
            dataframe[column_name] = pd.to_numeric(dataframe[column_name], errors="coerce")

    if "income" in dataframe.columns:
        dataframe["log_income"] = np.log1p(dataframe["income"])

    late_columns = {"late_30_59", "late_60_89", "late_90"}
    if late_columns.issubset(dataframe.columns):
        dataframe["weighted_late_score"] = (
            dataframe["late_30_59"] * 1
            + dataframe["late_60_89"] * 2
            + dataframe["late_90"] * 4
        )

    return dataframe


def build_cleaned_dataframe(raw_path: str | Path = DEFAULT_RAW_EXCEL_PATH) -> tuple[pd.DataFrame, int]:
    raw_file = Path(raw_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw Excel file not found: {raw_file}")

    dataframe = pd.read_excel(raw_file)

    unnamed_columns = [column for column in dataframe.columns if str(column).lower().startswith("unnamed")]
    if unnamed_columns:
        dataframe = dataframe.drop(columns=unnamed_columns)

    seen_names: set[str] = set()
    dataframe.columns = [
        normalize_column_name(column_name, position, seen_names)
        for position, column_name in enumerate(dataframe.columns, start=1)
    ]

    before_dedup = len(dataframe)
    dataframe = dataframe.drop_duplicates().reset_index(drop=True)
    duplicates_removed = before_dedup - len(dataframe)
    dataframe = add_engineered_features(dataframe)
    return dataframe, duplicates_removed


def transform_raw_to_cleaned_excel(
    raw_path: str | Path = DEFAULT_RAW_EXCEL_PATH,
    cleaned_path: str | Path = DEFAULT_CLEANED_EXCEL_PATH,
) -> Path:
    dataframe, _ = build_cleaned_dataframe(raw_path)
    destination = Path(cleaned_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_excel(destination, index=False)
    return destination
