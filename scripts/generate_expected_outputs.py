from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.io_helpers import load_yaml, read_json


def main() -> None:
    config = load_yaml("configs/app_config.yaml")
    output_dir = Path(config["paths"]["output_dir"])

    joined = pd.read_csv(output_dir / "customer_order_360.csv")
    validation = read_json(output_dir / "validation_report.json")
    benchmark_path = output_dir / "performance_benchmark.json"
    benchmark = read_json(benchmark_path) if benchmark_path.exists() else {}

    preview = joined.head(5).to_markdown(index=False)
    status_counts = joined["normalized_status"].value_counts().to_dict()

    content = f"""# Expected Outputs

## 1. Joined Dataset Preview

{preview}

## 2. Dataset Stats

- Total joined records: {len(joined)}
- Unique customers: {joined['customer_id'].nunique()}
- Total revenue: {round(joined['order_amount'].sum(), 2)}
- Normalized status counts: {status_counts}

## 3. Agentic Validation Summary

- Validation agent: {validation['summary'].get('validation_agent')}
- Passed rule checks: {validation['summary']['passed_rule_checks']} / {validation['summary']['total_rule_checks']}
- Semantic name pass rate: {validation['summary']['semantic_name_pass_rate']}
- Semantic status pass rate: {validation['summary']['semantic_status_pass_rate']}
- LLM records checked: {validation['summary'].get('llm_records_checked')}
- LLM records equivalent: {validation['summary'].get('llm_records_equivalent')}
- LLM mode: {validation.get('llm_semantic_checks', [{}])[0].get('result', {}).get('mode', 'not_run')}

## 4. Performance Benchmark

- Baseline seconds: {benchmark.get('baseline_seconds', 'not generated')}
- Optimized seconds: {benchmark.get('optimized_seconds', 'not generated')}
- Throughput improvement percent: {benchmark.get('throughput_improvement_pct', 'not generated')}
- Processing cost reduction proxy percent: {benchmark.get('processing_cost_reduction_proxy_pct', 'not generated')}

## 5. Files Produced

- `data/output/migrated_customers.parquet`
- `data/output/migrated_orders.parquet`
- `data/output/customer_order_360.parquet`
- `data/output/customer_order_360.csv`
- `data/output/validation_report.json`
- `data/output/validation_summary.txt`
- `data/output/performance_benchmark.json`
- `data/output/expected_outputs.md`
"""

    with open(output_dir / "expected_outputs.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("Generated expected outputs documentation")


if __name__ == "__main__":
    main()
