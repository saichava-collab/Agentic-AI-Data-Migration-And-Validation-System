from __future__ import annotations

import json
import time
from datetime import datetime

from kafka import KafkaProducer

from utils.io_helpers import load_yaml


EVENTS = [
    {"order_id": 2001, "customer_id": 1, "product_name": "Tablet", "amount": 650.0, "status": "DONE"},
    {"order_id": 2002, "customer_id": 3, "product_name": "Headphones", "amount": 180.0, "status": "PENDING_APPROVAL"},
    {"order_id": 2003, "customer_id": 5, "product_name": "Microphone", "amount": 120.0, "status": "FAILED"},
]


def main() -> None:
    config = load_yaml("configs/app_config.yaml")
    kafka_cfg = config["kafka"]

    producer = KafkaProducer(
        bootstrap_servers=kafka_cfg["bootstrap_servers"],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )

    for event in EVENTS:
        payload = {**event, "event_ts": datetime.utcnow().isoformat()}
        producer.send(kafka_cfg["topic"], payload)
        print(f"Published event: {payload}")
        time.sleep(1)

    producer.flush()
    producer.close()
    print("Kafka publishing complete")


if __name__ == "__main__":
    main()
