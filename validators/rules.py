from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass
class ValidationResult:
    name: str
    passed: bool
    details: Dict[str, object]


class RuleValidator:
    def check_row_count(self, source_count: int, target_count: int, name: str) -> ValidationResult:
        return ValidationResult(
            name=name,
            passed=source_count == target_count,
            details={"source_count": source_count, "target_count": target_count},
        )

    def check_no_duplicates(self, df: pd.DataFrame, columns: List[str], name: str) -> ValidationResult:
        duplicate_count = int(df.duplicated(subset=columns).sum())
        return ValidationResult(
            name=name,
            passed=duplicate_count == 0,
            details={"duplicate_count": duplicate_count, "columns": columns},
        )

    def check_not_null(self, df: pd.DataFrame, columns: List[str], name: str) -> ValidationResult:
        null_counts = {column: int(df[column].isna().sum()) for column in columns}
        passed = all(count == 0 for count in null_counts.values())
        return ValidationResult(name=name, passed=passed, details={"null_counts": null_counts})
