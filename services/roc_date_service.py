"""ROC date conversion service."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


class RocDateError(ValueError):
    """Raised when a ROC date cannot be parsed or validated."""


@dataclass(frozen=True)
class RocDateService:
    """Convert Taiwan ROC dates to Gregorian dates."""

    _pattern = re.compile(
        r"^\s*(?P<year>\d{1,3})\s*(?P<sep>[\/\-.\*]|年)\s*"
        r"(?P<month>\d{1,2})\s*(?(sep)(?:月|(?P=sep)))\s*"
        r"(?P<day>\d{1,2})\s*(?:日)?\s*$"
    )

    def convert(self, raw_value: str) -> str:
        """Convert a ROC date string into a Gregorian date string."""
        if not raw_value or not raw_value.strip():
            raise RocDateError("請輸入民國日期，例如：92/4/21。")

        normalized = raw_value.strip()
        if "年" in normalized:
            match = re.match(
                r"^\s*(\d{1,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日?\s*$",
                normalized,
            )
            if not match:
                raise RocDateError("日期格式不正確，請使用例如：92年4月21日。")
            year_text, month_text, day_text = match.groups()
            return self._format(year_text, month_text, day_text)

        match = re.match(
            r"^\s*(\d{1,3})\s*([\/\-.\*])\s*(\d{1,2})\s*\2\s*(\d{1,2})\s*$",
            normalized,
        )
        if not match:
            raise RocDateError("日期格式不正確，支援 /、-、.、* 或 年月日。")
        year_text, _, month_text, day_text = match.groups()
        return self._format(year_text, month_text, day_text)

    def _format(self, year_text: str, month_text: str, day_text: str) -> str:
        year = int(year_text) + 1911
        month = int(month_text)
        day = int(day_text)
        try:
            date(year, month, day)
        except ValueError as exc:
            raise RocDateError("日期不存在，請確認年月日是否正確。") from exc
        return f"{year}/{month_text}/{day_text}"
