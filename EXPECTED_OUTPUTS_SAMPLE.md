# Expected Outputs Sample - v3 Ollama Edition

This is a representative sample of what you should see after running:

```bash
export PYTHONPATH=$(pwd)
./run_all.sh
```

## Terminal Summary

```text
Created CSV source at: data/source_csv/customers.csv
Created SQLite source at: data/source_sqlite.db
Customers rows: 6
Orders rows: 8
Batch migration completed successfully
Migrated customers: 6
Migrated orders: 8
Joined customer-order records: 8
Baseline seconds: <machine-specific>
Optimized seconds: <machine-specific>
Measured throughput improvement: <machine-specific>%
Agentic validation completed successfully
Validation summary written to data/output/validation_summary.txt
Generated expected outputs documentation
All batch steps completed successfully
```

## Important Files

```text
data/source_csv/customers.csv
data/source_sqlite.db
data/output/migrated_customers.parquet
data/output/migrated_orders.parquet
data/output/customer_order_360.parquet
data/output/customer_order_360.csv
data/output/validation_report.json
data/output/validation_summary.txt
data/output/performance_benchmark.json
data/output/expected_outputs.md
```

## validation_summary.txt Example

```text
Validation Summary
==================
Validation agent: MigrationValidationAgent
Rule checks passed: 4 / 4
Semantic name pass rate: 1.0
Semantic status pass rate: 1.0
LLM records checked: 3
LLM records equivalent: 3
LLM mode: ollama
```

If Ollama is running and the model is installed, `LLM mode` should be `ollama`. If Ollama is not running, the pipeline still finishes with `LLM mode: offline-fallback`.

## performance_benchmark.json Example

```json
{
  "baseline_strategy": "default Spark execution plan",
  "optimized_strategy": "repartition by customer_id and cache before downstream actions",
  "baseline_seconds": 1.2345,
  "optimized_seconds": 0.8123,
  "baseline_records": 8,
  "optimized_records": 8,
  "throughput_improvement_pct": 34.23,
  "processing_cost_reduction_proxy_pct": 34.23,
  "note": "Runtime varies by machine. The file documents the exact local measurement for interview discussion."
}
```

## customer_order_360.csv Preview

```text
customer_id,full_name,email,country,signup_ts,order_id,product_name,order_amount,order_status,normalized_status,created_at
1,Alice Johnson,alice@example.com,USA,2024-01-10 10:15:00,1001,Laptop,1200.0,DONE,completed,2024-02-01 08:00:00
1,Alice Johnson,alice@example.com,USA,2024-01-10 10:15:00,1002,Mouse,25.5,PENDING_APPROVAL,pending,2024-02-01 09:00:00
2,Bob Smith,bob.smith@example.com,USA,2024-01-11 12:00:00,1003,Keyboard,70.0,DONE,completed,2024-02-02 10:00:00
```
