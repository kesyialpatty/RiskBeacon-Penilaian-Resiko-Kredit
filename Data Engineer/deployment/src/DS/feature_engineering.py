import numpy as np
import pandas as pd


# ── Konstanta clipping dari training ──────────────────────────
CLIP_BOUNDS = {
    "revolving_utilization_pct": (0.0, 1.09393041),
    "debt_ratio":                (0.0, 4985.24),
    "income":                    (0.0, 23085.4),
}

COUNT_CLIP_MAX = 10

HF_FEATURE_COLUMNS = [
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
    "disposable_income",
    "log_debt_ratio",
]

MODEL_FEATURE_COLUMNS = [
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberRealEstateLoansOrLines",
    "NumberOfDependents",
    "WeightedLateScore",
    "LogIncome",
    "DisposableIncome",
    "LogDebtRatio",
]

DISPLAY_LABELS = {
    "revolving_utilization_pct": "Revolving Utilization",
    "age":                       "Age",
    "late_30_59":                "Late 30-59 Days",
    "debt_ratio":                "Debt Ratio",
    "income":                    "Monthly Income",
    "open_loans":                "Open Credit Lines and Loans",
    "late_90":                   "Late 90 Days",
    "real_estate_loans":         "Real Estate Loans",
    "late_60_89":                "Late 60-89 Days",
    "dependents":                "Dependents",
    "log_income":                "Log Income",
    "weighted_late_score":       "Weighted Late Score",
    "disposable_income":         "Disposable Income",
    "log_debt_ratio":            "Log Debt Ratio",
}


def build_feature_frame(
    *,
    age,
    revolving_utilization_pct,
    debt_ratio,
    income,
    open_loans,
    real_estate_loans,
    dependents,
    late_30_59,
    late_60_89,
    late_90,
):
    record = {
        "revolving_utilization_pct": float(revolving_utilization_pct),
        "age":                       int(age),
        "late_30_59":                int(late_30_59),
        "debt_ratio":                float(debt_ratio),
        "income":                    float(income),
        "open_loans":                int(open_loans),
        "late_90":                   int(late_90),
        "real_estate_loans":         int(real_estate_loans),
        "late_60_89":                int(late_60_89),
        "dependents":                float(dependents),
    }
    record["log_income"]          = float(np.log1p(record["income"]))
    record["weighted_late_score"] = (
        record["late_30_59"] * 1
        + record["late_60_89"] * 2
        + record["late_90"] * 4
    )
    record["disposable_income"]   = float(record["income"] * (1 - record["debt_ratio"]))
    record["log_debt_ratio"]      = float(np.log1p(record["debt_ratio"]))

    return pd.DataFrame([record], columns=HF_FEATURE_COLUMNS)


def build_model_feature_frame(features):
    row = features.iloc[0]

    # ── Clipping continuous (batas dari quantile 1%-99% training) ──
    util = float(np.clip(
        row["revolving_utilization_pct"],
        CLIP_BOUNDS["revolving_utilization_pct"][0],
        CLIP_BOUNDS["revolving_utilization_pct"][1],
    ))
    debt = float(np.clip(
        row["debt_ratio"],
        CLIP_BOUNDS["debt_ratio"][0],
        CLIP_BOUNDS["debt_ratio"][1],
    ))
    inc = float(np.clip(
        row["income"],
        CLIP_BOUNDS["income"][0],
        CLIP_BOUNDS["income"][1],
    ))

    # ── Clipping count columns ke [0, 10] ──────────────────────────
    open_loans    = int(np.clip(row["open_loans"],       0, COUNT_CLIP_MAX))
    real_estate   = int(np.clip(row["real_estate_loans"], 0, COUNT_CLIP_MAX))
    dependents    = float(np.clip(row["dependents"],     0, COUNT_CLIP_MAX))
    late_30_59    = int(np.clip(row["late_30_59"],       0, COUNT_CLIP_MAX))
    late_60_89    = int(np.clip(row["late_60_89"],       0, COUNT_CLIP_MAX))
    late_90       = int(np.clip(row["late_90"],          0, COUNT_CLIP_MAX))

    # ── Derived features (identik dengan training) ─────────────────
    util_log          = float(np.log1p(util))        # log1p SETELAH clip
    weighted_late     = late_30_59 * 1 + late_60_89 * 2 + late_90 * 4
    log_income        = float(np.log1p(inc))
    disposable_income = float(inc * (1 - debt))
    log_debt_ratio    = float(np.log1p(debt))

    model_record = {
        "RevolvingUtilizationOfUnsecuredLines": util_log,
        "age":                                  int(row["age"]),
        "NumberOfOpenCreditLinesAndLoans":      open_loans,
        "NumberRealEstateLoansOrLines":         real_estate,
        "NumberOfDependents":                   dependents,
        "WeightedLateScore":                    float(weighted_late),
        "LogIncome":                            log_income,
        "DisposableIncome":                     disposable_income,
        "LogDebtRatio":                         log_debt_ratio,
    }
    return pd.DataFrame([model_record], columns=MODEL_FEATURE_COLUMNS)


def build_display_frame(features):
    display_frame = features.copy()
    return display_frame.rename(columns=DISPLAY_LABELS)
