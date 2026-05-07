from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from pipeline.extract_excel import DEFAULT_RAW_EXCEL_PATH, extract_to_raw_excel
from pipeline.transform_excel import DEFAULT_CLEANED_EXCEL_PATH, transform_raw_to_cleaned_excel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_SRC_PATH = PROJECT_ROOT / "deployment" / "src"
if str(DEPLOYMENT_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT_SRC_PATH))

from gx_validation import validate_csv_with_gx  # noqa: E402


def _resolve_paths() -> tuple[Path | None, Path, Path]:
    source_env = os.environ.get("SOURCE_FILE_PATH", "").strip()
    source_path = Path(source_env) if source_env else None

    raw_env = os.environ.get("RAW_EXCEL_PATH", "").strip()
    cleaned_env = os.environ.get("CLEANED_EXCEL_PATH", "").strip()
    raw_path = Path(raw_env) if raw_env else DEFAULT_RAW_EXCEL_PATH
    cleaned_path = Path(cleaned_env) if cleaned_env else DEFAULT_CLEANED_EXCEL_PATH
    return source_path, raw_path, cleaned_path


def check_source_or_raw_ready() -> bool:
    source_path, raw_path, _ = _resolve_paths()

    if source_path and source_path.exists():
        print(f"[check] source file is available: {source_path}")
        return True

    if raw_path.exists():
        print(f"[check] source file is not set/found, using existing raw Excel: {raw_path}")
        return True

    raise FileNotFoundError(
        f"No valid input found. Set SOURCE_FILE_PATH or provide raw file at {raw_path}"
    )


def extract_raw_excel_task() -> str:
    source_path, raw_path, _ = _resolve_paths()

    if source_path and source_path.exists():
        output = extract_to_raw_excel(source_path, raw_path)
        print(f"[extract] raw Excel saved to: {output}")
        return str(output)

    if raw_path.exists():
        print(f"[extract] skipped. Reusing existing raw Excel: {raw_path}")
        return str(raw_path)

    raise FileNotFoundError("Extract step cannot run because source and raw Excel are both unavailable.")


def transform_cleaned_excel_task() -> str:
    _, raw_path, cleaned_path = _resolve_paths()
    output = transform_raw_to_cleaned_excel(raw_path, cleaned_path)
    print(f"[transform] cleaned Excel saved to: {output}")
    return str(output)


def validate_cleaned_excel_task() -> str:
    _, _, cleaned_path = _resolve_paths()

    try:
        validation_payload = validate_csv_with_gx(cleaned_path)
        statistics = validation_payload.get("statistics", {})
        print("[validate] GX validation statistics:")
        print(json.dumps(statistics, indent=2))
        return str(validation_payload.get("results_path"))
    except ModuleNotFoundError:
        message = "Great Expectations is not installed in this Airflow environment."
        print(f"[validate] skipped. {message}")
        return message

