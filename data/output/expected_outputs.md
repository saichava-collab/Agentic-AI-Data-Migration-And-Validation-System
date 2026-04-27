# Expected Outputs

## 1. Joined Dataset Preview

|   customer_id | full_name    | email                 | country   | signup_ts           |   order_id | product_name   |   order_amount | order_status     | normalized_status   | created_at          |
|--------------:|:-------------|:----------------------|:----------|:--------------------|-----------:|:---------------|---------------:|:-----------------|:--------------------|:--------------------|
|             6 | Farhan Ali   | farhan@example.com    | UAE       | 2024-01-15 18:20:00 |       1007 | Dock           |            180 | DONE             | completed           | 2024-02-06 14:30:00 |
|             2 | Bob Smith    | bob.smith@example.com | USA       | 2024-01-11 12:00:00 |       1003 | Keyboard       |             70 | DONE             | completed           | 2024-02-02 10:00:00 |
|             4 | Diana Prince | diana@example.com     | India     | 2024-01-13 14:40:00 |       1005 | Desk           |            500 | DONE             | completed           | 2024-02-04 12:30:00 |
|             5 | Evelyn Stone | evelyn@example.com    | UK        | 2024-01-14 17:05:00 |       1006 | Chair          |            220 | PENDING_APPROVAL | pending             | 2024-02-05 13:30:00 |
|             2 | Bob Smith    | bob.smith@example.com | USA       | 2024-01-11 12:00:00 |       1008 | Webcam         |             95 | DONE             | completed           | 2024-02-07 15:30:00 |

## 2. Dataset Stats

- Total joined records: 8
- Unique customers: 6
- Total revenue: 2590.5
- Normalized status counts: {'completed': 5, 'pending': 2, 'cancelled': 1}

## 3. Agentic Validation Summary

- Validation agent: MigrationValidationAgent
- Passed rule checks: 4 / 4
- Semantic name pass rate: 0.1667
- Semantic status pass rate: 0.375
- LLM records checked: 3
- LLM records equivalent: 3
- LLM mode: ollama

## 4. Performance Benchmark

- Baseline seconds: 0.4592
- Optimized seconds: 0.3252
- Throughput improvement percent: 29.18
- Processing cost reduction proxy percent: 29.18

## 5. Files Produced

- `data/output/migrated_customers.parquet`
- `data/output/migrated_orders.parquet`
- `data/output/customer_order_360.parquet`
- `data/output/customer_order_360.csv`
- `data/output/validation_report.json`
- `data/output/validation_summary.txt`
- `data/output/performance_benchmark.json`
- `data/output/expected_outputs.md`
