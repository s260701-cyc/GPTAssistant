"""Tests for ROC date conversion."""

from __future__ import annotations

import pytest

from services.roc_date_service import RocDateError, RocDateService


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("92/4/21", "2003/4/21"),
        ("92/04/21", "2003/04/21"),
        ("112/12/31", "2023/12/31"),
        ("92年4月21日", "2003/4/21"),
        ("92.4.21", "2003/4/21"),
        ("92-4-21", "2003/4/21"),
        ("92*4*21", "2003/4/21"),
    ],
)
def test_convert_supported_formats(raw_value: str, expected: str) -> None:
    """Supported ROC date formats convert to Gregorian dates."""
    assert RocDateService().convert(raw_value) == expected


@pytest.mark.parametrize("raw_value", ["", "abc", "92/13/1", "92/2/30", "92_4_21"])
def test_convert_invalid_values(raw_value: str) -> None:
    """Invalid values raise friendly ROC date errors."""
    with pytest.raises(RocDateError):
        RocDateService().convert(raw_value)
