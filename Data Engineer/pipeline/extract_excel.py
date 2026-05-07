from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_EXCEL_PATH = PROJECT_ROOT / "data" / "raw_cs_training.xlsx"


def _read_tabular_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported source format: {path.suffix}")


def extract_to_raw_excel(source_path: str | Path, output_path: str | Path = DEFAULT_RAW_EXCEL_PATH) -> Path:
    source = Path(source_path)
    destination = Path(output_path)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    dataframe = _read_tabular_file(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_excel(destination, index=False)
    return destination
