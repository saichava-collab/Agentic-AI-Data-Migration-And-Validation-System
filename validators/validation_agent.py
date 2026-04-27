from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from validators.llm_validator import LLMValidator
from validators.rules import RuleValidator
from validators.semantic_validator import SemanticValidator


class MigrationValidationAgent:
    """
    Agent-style coordinator for migration validation.

    The agent runs three validation stages:
    1. deterministic rule checks,
    2. local semantic checks,
    3. optional real LLM record equivalence checks.
    """

    def __init__(
        self,
        semantic_threshold: float = 0.72,
        llm_enabled: bool | None = True,
        llm_model: str = "llama3",
        llm_base_url: str = "http://localhost:11434",
    ):
        self.rule_validator = RuleValidator()
        self.semantic_validator = SemanticValidator(semantic_threshold)
        self.llm_validator = LLMValidator(model=llm_model, base_url=llm_base_url, enabled=llm_enabled)

    def validate_dataset(self, customers_src, orders_src, target_joined) -> Dict[str, Any]:
        rule_results = [
            self.rule_validator.check_row_count(len(customers_src), target_joined["customer_id"].nunique(), "customer_count_match"),
            self.rule_validator.check_row_count(len(orders_src), len(target_joined), "order_count_match"),
            self.rule_validator.check_no_duplicates(target_joined[["customer_id"]].drop_duplicates(), ["customer_id"], "no_duplicate_customer_ids"),
            self.rule_validator.check_not_null(target_joined, ["customer_id", "order_id", "email"], "critical_fields_not_null"),
        ]

        source_name_pairs = list(
            zip(
                customers_src["full_name"].astype(str).tolist(),
                target_joined.drop_duplicates(subset=["customer_id"])["full_name"].astype(str).tolist(),
            )
        )
        status_pairs = list(
            zip(
                orders_src["order_status"].astype(str).tolist(),
                target_joined["normalized_status"].astype(str).tolist(),
            )
        )

        name_comparisons = self.semantic_validator.batch_compare(source_name_pairs)
        status_comparisons = self.semantic_validator.batch_compare(status_pairs)

        # Sample records are enough for a portfolio demo and avoid unnecessary LLM cost.
        llm_samples: List[Dict[str, Any]] = []
        for _, target_row in target_joined.head(3).iterrows():
            order_id = int(target_row["order_id"])
            customer_id = int(target_row["customer_id"])
            source_order = orders_src[orders_src["order_id"] == order_id].iloc[0].to_dict()
            source_customer = customers_src[customers_src["customer_id"] == customer_id].iloc[0].to_dict()
            source_record = {"customer": source_customer, "order": source_order}
            target_record = target_row.to_dict()
            llm_result = self.llm_validator.compare_records(source_record, target_record)
            llm_samples.append(
                {
                    "source_order_id": order_id,
                    "source_customer_id": customer_id,
                    "result": self.llm_validator.to_dict(llm_result),
                }
            )

        return {
            "summary": {
                "total_rule_checks": len(rule_results),
                "passed_rule_checks": sum(1 for r in rule_results if r.passed),
                "failed_rule_checks": sum(1 for r in rule_results if not r.passed),
                "semantic_name_pass_rate": round(sum(1 for x in name_comparisons if x.passed) / len(name_comparisons), 4),
                "semantic_status_pass_rate": round(sum(1 for x in status_comparisons if x.passed) / len(status_comparisons), 4),
                "llm_records_checked": len(llm_samples),
                "llm_records_equivalent": sum(1 for sample in llm_samples if sample["result"]["equivalent"]),
                "validation_agent": "MigrationValidationAgent",
            },
            "rules": [{"name": r.name, "passed": r.passed, "details": r.details} for r in rule_results],
            "semantic_checks": {
                "names": [asdict(comparison) for comparison in name_comparisons],
                "statuses": [asdict(comparison) for comparison in status_comparisons],
            },
            "llm_semantic_checks": llm_samples,
        }
