# Agentic AI Data Migration & Validation System

An end-to-end data engineering project that demonstrates distributed ETL/ELT migration, orchestration, streaming ingestion, agentic validation, **free local LLM semantic comparison using Ollama**, and measurable performance benchmarking.

- **Spark ETL/ELT migration** across heterogeneous sources: CSV + SQLite
- **Airflow orchestration** for the batch migration workflow
- **Kafka event streaming** for real-time ingestion and monitoring
- **Agentic validation workflow** via `MigrationValidationAgent`
- **LLM-based semantic comparison** using Ollama locally, with `llama3` by default
- **No API keys and no paid LLM dependency**
- **Offline fallback validation** if Ollama is not running, so the rest of the project still executes
- **Performance benchmark artifact** showing baseline vs optimized Spark execution
- **Expected output generation** for demo/interview discussion

## Architecture

```text
CSV customers + SQLite orders
        |
        v
PySpark batch migration
        |
        v
Normalized parquet + CSV target datasets
        |
        v
MigrationValidationAgent
  - rule checks
  - local semantic comparison
  - Ollama LLM semantic equivalence checks
        |
        v
validation_report.json + validation_summary.txt

Kafka producer -> Kafka topic -> Kafka stream processor -> streaming metrics

Airflow DAG -> setup -> migration -> validation -> expected outputs
```

## Project Structure

```text
agentic_ai_data_migration_validation_system/
├── airflow/dags/migration_validation_dag.py
├── configs/app_config.yaml
├── jobs/batch_migration.py
├── scripts/setup_demo.py
├── scripts/check_ollama.py
├── scripts/generate_expected_outputs.py
├── services/kafka_producer.py
├── services/kafka_stream_processor.py
├── utils/io_helpers.py
├── validators/llm_validator.py
├── validators/rules.py
├── validators/semantic_validator.py
├── validators/validation_agent.py
├── validators/run_validation.py
├── tests/test_rules.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── run_all.sh
└── README.md
```

## Mac Setup

Use Python 3.11 for best compatibility with PySpark and Airflow.

```bash
brew install python@3.11 openjdk@17 ollama
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="/opt/homebrew/opt/python@3.11/bin:$JAVA_HOME/bin:$PATH"
```

Verify:

```bash
python3.11 --version
java -version
ollama --version
```

## Start Ollama and Pull a Free Local Model

In one terminal, start Ollama:

```bash
ollama serve
```

In another terminal, pull the default model:

```bash
ollama pull llama3
```

If your Mac is slower, you can use Mistral instead:

```bash
ollama pull mistral
export OLLAMA_MODEL=mistral
```

Check that Ollama is ready:

```bash
python scripts/check_ollama.py
```

Expected successful output:

```text
Ollama is ready. Model available: llama3
```

## Local Batch Run

From the project folder:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
export PYTHONPATH=$(pwd)
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run all batch steps:

```bash
./run_all.sh
```

Or run step by step:

```bash
python scripts/setup_demo.py
python jobs/batch_migration.py
python validators/run_validation.py
python scripts/generate_expected_outputs.py
```

## Confirm Real Ollama LLM Validation

After running validation:

```bash
cat data/output/validation_summary.txt
```

Look for:

```text
LLM mode: ollama
```

You can also inspect the detailed report:

```bash
cat data/output/validation_report.json
```

If Ollama is not running, the project will still finish, but the summary will show:

```text
LLM mode: offline-fallback
```

To make the resume claim fully authentic, run Ollama and confirm the mode is `ollama`.

## Expected Batch Outputs

After running the batch pipeline, check:

```bash
find data -type f
```

Important files:

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

Preview outputs:

```bash
head -20 data/output/customer_order_360.csv
cat data/output/validation_summary.txt
cat data/output/performance_benchmark.json
cat data/output/expected_outputs.md
```

## Performance Benchmark

`jobs/batch_migration.py` measures:

- baseline Spark execution time
- optimized Spark execution time
- throughput improvement percentage
- processing-cost-reduction proxy percentage

The benchmark is written to:

```text
data/output/performance_benchmark.json
```

Important note: local benchmark numbers vary by laptop. The value of this feature is that you have a reproducible artifact to discuss in interviews instead of making an unsupported performance claim.

## Kafka Streaming Run

Start Docker Desktop first.

```bash
docker compose up -d zookeeper kafka
```

Create the topic:

```bash
docker exec -it agentic-kafka kafka-topics.sh --create \
  --topic migration-events \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1
```

Terminal 1:

```bash
source .venv/bin/activate
export PYTHONPATH=$(pwd)
python services/kafka_stream_processor.py
```

Terminal 2:

```bash
source .venv/bin/activate
export PYTHONPATH=$(pwd)
python services/kafka_producer.py
```

Expected streaming outputs:

```text
data/streaming/processed_events.jsonl
data/streaming/stream_metrics.json
```

Inspect:

```bash
cat data/streaming/stream_metrics.json
tail -n 20 data/streaming/processed_events.jsonl
```

## Airflow Run

Start Docker Desktop first.

```bash
docker compose up -d airflow-init airflow-webserver airflow-scheduler
```

Open:

```text
http://localhost:8080
```

Login:

```text
username: airflow
password: airflow
```

Trigger DAG:

```text
agentic_data_migration_validation
```

## Tests

```bash
export PYTHONPATH=$(pwd)
pytest -q
```


## Clean Restart

```bash
rm -rf data/output data/streaming data/source_csv data/source_sqlite.db
mkdir -p data/output data/streaming data/source_csv
./run_all.sh
```
