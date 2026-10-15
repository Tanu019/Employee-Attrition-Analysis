"""
Data Loader Module for Employee Attrition Analysis.
Handles multi-sheet Excel files and CSV uploads with caching and fingerprinting.
"""
import io
import hashlib
from pathlib import Path
from typing import Dict, Union, Tuple, Optional
import pandas as pd

from config.settings import DEFAULT_DATA_FILE

# Global in-memory cache to prevent redundant disk/XML parsing
_CACHED_WORKBOOK: Optional[Dict[str, pd.DataFrame]] = None
_CACHED_FINGERPRINT: Optional[str] = None
_CACHED_MASTER_DF: Optional[pd.DataFrame] = None


def compute_file_fingerprint(data_bytes: bytes) -> str:
    """Compute SHA-256 fingerprint of file bytes for version tracking."""
    return hashlib.sha256(data_bytes).hexdigest()[:12]


def load_workbook_data(
    file_source: Union[str, Path, io.BytesIO, bytes] = DEFAULT_DATA_FILE
) -> Tuple[Dict[str, pd.DataFrame], str]:
    """
    Load all sheets from an Excel workbook or single CSV into a dictionary of DataFrames.
    Returns: (dict_of_dataframes, fingerprint)
    """
    global _CACHED_WORKBOOK, _CACHED_FINGERPRINT

    # If loading default data file and already cached in memory, return cache
    if file_source == DEFAULT_DATA_FILE and _CACHED_WORKBOOK is not None and _CACHED_FINGERPRINT is not None:
        return _CACHED_WORKBOOK, _CACHED_FINGERPRINT

    if isinstance(file_source, (str, Path)):
        path = Path(file_source)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found at: {path}")
        with open(path, "rb") as f:
            raw_bytes = f.read()
        filename = path.name
    elif isinstance(file_source, io.BytesIO):
        raw_bytes = file_source.getvalue()
        filename = getattr(file_source, "name", "uploaded_file.xlsx")
    elif isinstance(file_source, bytes):
        raw_bytes = file_source
        filename = "bytes_dataset.xlsx"
    else:
        raise ValueError("Unsupported file source format.")

    fingerprint = compute_file_fingerprint(raw_bytes)
    data_dict: Dict[str, pd.DataFrame] = {}

    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(raw_bytes))
        data_dict["Employee Master"] = df
        return data_dict, fingerprint

    # Process Excel workbook
    buffer = io.BytesIO(raw_bytes)
    excel_file = pd.ExcelFile(buffer)
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        data_dict[sheet_name] = df

    # Cache if default file
    if file_source == DEFAULT_DATA_FILE:
        _CACHED_WORKBOOK = data_dict
        _CACHED_FINGERPRINT = fingerprint

    return data_dict, fingerprint


def get_default_master_data() -> pd.DataFrame:
    """Convenience helper to retrieve Employee Master DataFrame from default dataset with instant caching."""
    global _CACHED_MASTER_DF
    if _CACHED_MASTER_DF is not None:
        return _CACHED_MASTER_DF

    if _CACHED_WORKBOOK is not None and "Employee Master" in _CACHED_WORKBOOK:
        _CACHED_MASTER_DF = _CACHED_WORKBOOK["Employee Master"]
        return _CACHED_MASTER_DF

    # Fast path: load only the Employee Master sheet
    df = pd.read_excel(DEFAULT_DATA_FILE, sheet_name="Employee Master")
    _CACHED_MASTER_DF = df
    return df
