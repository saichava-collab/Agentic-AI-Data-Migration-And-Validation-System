import pandas as pd

from validators.rules import RuleValidator


def test_check_row_count_passes():
    validator = RuleValidator()
    result = validator.check_row_count(3, 3, "row_count")
    assert result.passed is True


def test_check_no_duplicates_fails_when_duplicates_exist():
    validator = RuleValidator()
    df = pd.DataFrame({"customer_id": [1, 1, 2]})
    result = validator.check_no_duplicates(df, ["customer_id"], "duplicate_check")
    assert result.passed is False
    assert result.details["duplicate_count"] == 1
