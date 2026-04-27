from __future__ import annotations

import json
from datetime import datetime

from kafka import KafkaConsumer

from utils.io_helpers import append_jsonl, load_yaml, write_json


STATUS_MAPPING = {
    "DONE": "completed",
    "PENDING_APPROVAL": "pending",
    "FAILED": "cancelled",
}


def main() -> None:
    config = load_yaml("configs/app_config.yaml")
    kafka_cfg = config["kafka"]
    streaming_dir = config["paths"]["streaming_dir"]

    consumer = KafkaConsumer(
        kafka_cfg["topic"],
        bootstrap_servers=kafka_cfg["bootstrap_servers"],
        auto_offset_reset="earliest",
        group_id=kafka_cfg["consumer_group"],
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    metrics = {"events_processed": 0, "success_count": 0, "failure_count": 0, "last_processed_at": None}

    print("Listening for Kafka events...")
    for message in consumer:
        try:
            event = message.value
            transformed = {
                **event,
                "normalized_status": STATUS_MAPPING.get(event["status"], "unknown"),
                "processed_at": datetime.utcnow().isoformat(),
            }
            append_jsonl(f"{streaming_dir}/processed_events.jsonl", transformed)
            metrics["events_processed"] += 1
            metrics["success_count"] += 1
            metrics["last_processed_at"] = transformed["processed_at"]
            write_json(f"{streaming_dir}/stream_metrics.json", metrics)
            print(f"Processed event: {transformed}")
        except Exception as exc:  # noqa: BLE001
            metrics["events_processed"] += 1
            metrics["failure_count"] += 1
            write_json(f"{streaming_dir}/stream_metrics.json", metrics)
            print(f"Failed to process event: {exc}")


if __name__ == "__main__":
    main()
