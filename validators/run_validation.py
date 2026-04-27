from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from utils.io_helpers import load_yaml, write_json
from validators.validation_agent import MigrationValidationAgent


def main() -> None:
    config = load_yaml("configs/app_config.yaml")
    paths = config["paths"]
    validation_cfg = config["validation"]
    output_dir = Path(paths["output_dir"])

    customers_src = pd.read_csv(paths["source_csv"])

    conn = sqlite3.connect(paths["source_sqlite"])
    try:
        orders_src = pd.read_sql_query("SELECT * FROM orders", conn)
    finally:
        conn.close()

    target_joined = pd.read_csv(output_dir / "customer_order_360.csv")

    agent = MigrationValidationAgent(
        semantic_threshold=validation_cfg["semantic_similarity_threshold"],
        llm_enabled=validation_cfg.get("enable_llm_validation", True),
        llm_model=validation_cfg.get("ollama_model", "llama3"),
        llm_base_url=validation_cfg.get("ollama_base_url", "http://localhost:11434"),
    )
    report = agent.validate_dataset(customers_src, orders_src, target_joined)

    write_json(output_dir / "validation_report.json", report)

    lines = [
        "Validation Summary",
        "==================",
        f"Validation agent: {report['summary']['validation_agent']}",
        f"Rule checks passed: {report['summary']['passed_rule_checks']} / {report['summary']['total_rule_checks']}",
        f"Semantic name pass rate: {report['summary']['semantic_name_pass_rate']}",
        f"Semantic status pass rate: {report['summary']['semantic_status_pass_rate']}",
        f"LLM records checked: {report['summary']['llm_records_checked']}",
        f"LLM records equivalent: {report['summary']['llm_records_equivalent']}",
        f"LLM mode: {report['llm_semantic_checks'][0]['result']['mode'] if report['llm_semantic_checks'] else 'not_run'}",
    ]
    with open(output_dir / "validation_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("Agentic validation completed successfully")
    print("Validation summary written to data/output/validation_summary.txt")


if __name__ == "__main__":
    main()
