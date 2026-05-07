from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from extract_excel import DEFAULT_RAW_EXCEL_PATH, extract_to_raw_excel
from transform_excel import DEFAULT_CLEANED_EXCEL_PATH, transform_raw_to_cleaned_excel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_SRC_PATH = PROJECT_ROOT / "deployment" / "src"
if str(STREAMLIT_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_SRC_PATH))

from gx_validation import validate_default_cleaned_csv_with_gx  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local Excel pipeline (extract, transform, validate).")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Optional source file (.csv/.xlsx/.xls). If provided, it will be extracted to raw_cs_training.xlsx",
    )
    parser.add_argument(
        "--raw-path",
        type=str,
        default=str(DEFAULT_RAW_EXCEL_PATH),
        help="Raw Excel path.",
    )
    parser.add_argument(
        "--cleaned-path",
        type=str,
        default=str(DEFAULT_CLEANED_EXCEL_PATH),
        help="Cleaned Excel path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = Path(args.raw_path)
    cleaned_path = Path(args.cleaned_path)

    if args.source:
        extracted_path = extract_to_raw_excel(args.source, raw_path)
        print(f"[extract] raw Excel saved at: {extracted_path}")
    elif not raw_path.exists():
        raise FileNotFoundError(
            f"Raw Excel file not found at {raw_path}. Provide --source to build raw Excel from source data."
        )
    else:
        print(f"[extract] using existing raw Excel: {raw_path}")

    cleaned_output = transform_raw_to_cleaned_excel(raw_path, cleaned_path)
    print(f"[transform] cleaned Excel saved at: {cleaned_output}")

    try:
        validation_payload = validate_default_cleaned_csv_with_gx()
        stats = validation_payload.get("statistics", {})
        print("[validate] GX validation summary:")
        print(json.dumps(stats, indent=2))
        print(f"[validate] GX result file: {validation_payload.get('results_path')}")
    except ModuleNotFoundError:
        print("[validate] skipped because `great_expectations` is not installed yet.")
        print("[validate] install dependencies with: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
