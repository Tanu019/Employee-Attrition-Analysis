"""
Tests for data loader module.
"""
import pytest
from pathlib import Path
from src.data_loader import load_workbook_data, compute_file_fingerprint, get_default_master_data
from config.settings import DEFAULT_DATA_FILE


def test_default_file_exists():
    assert Path(DEFAULT_DATA_FILE).exists(), f"Default dataset file missing at {DEFAULT_DATA_FILE}"


def test_load_workbook_data():
    workbook, fingerprint = load_workbook_data(DEFAULT_DATA_FILE)
    assert isinstance(workbook, dict)
    assert len(workbook) > 0
    assert "Employee Master" in workbook
    assert len(fingerprint) == 12

    master_df = workbook["Employee Master"]
    assert len(master_df) == 2500
    assert len(master_df.columns) == 70


def test_compute_file_fingerprint():
    data = b"Sample HR Workforce Test Bytes"
    fp1 = compute_file_fingerprint(data)
    fp2 = compute_file_fingerprint(data)
    assert fp1 == fp2
    assert len(fp1) == 12


def test_get_default_master_data():
    df = get_default_master_data()
    assert not df.empty
    assert len(df) == 2500
