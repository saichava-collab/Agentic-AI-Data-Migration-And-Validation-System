from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class LLMValidationResult:
    equivalent: bool
    confidence: float
    reason: str
    model: str
    mode: str
    provider: str


class LLMValidator:
    """
    Local LLM-powered semantic validator using Ollama.

    This project intentionally avoids paid API keys. When Ollama is running
    locally, the validator calls http://localhost:11434/api/generate and asks a
    local model such as llama3 or mistral to judge semantic equivalence between
    source and migrated records.

    If Ollama is not running, the class returns a deterministic fallback result
    so the rest of the pipeline remains runnable. The validation report records
    the mode as either `ollama` or `offline-fallback`.
    """

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        enabled: Optional[bool] = True,
        timeout_seconds: int = 120,
    ):
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url).rstrip("/")
        self.enabled = True if enabled is None else bool(enabled)
        self.timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", timeout_seconds))

    def _offline_compare(self, source_record: Dict[str, Any], target_record: Dict[str, Any], reason_prefix: str) -> LLMValidationResult:
        source_text = json.dumps(source_record, sort_keys=True, default=str).lower()
        target_text = json.dumps(target_record, sort_keys=True, default=str).lower()

        important_terms = ["completed", "pending", "cancelled", "customer", "order", "email", "amount", "status"]
        overlap = sum(1 for term in important_terms if term in source_text and term in target_text)
        confidence = min(0.95, 0.55 + overlap * 0.06)

        return LLMValidationResult(
            equivalent=confidence >= 0.70,
            confidence=round(confidence, 4),
            reason=f"{reason_prefix} Offline deterministic semantic overlap fallback was used.",
            model="offline-fallback",
            mode="offline-fallback",
            provider="local",
        )

    def _build_prompt(self, source_record: Dict[str, Any], target_record: Dict[str, Any]) -> str:
        return f"""
You are a data migration validation agent. Compare the source record and migrated target record.
Determine whether they are semantically equivalent after expected transformations such as trimming,
case normalization, status mapping, schema renaming, and timestamp casting.

Source record:
{json.dumps(source_record, indent=2, default=str)}

Migrated target record:
{json.dumps(target_record, indent=2, default=str)}

Return strict JSON only. Do not include markdown. Use exactly these keys:
{{
  "equivalent": true,
  "confidence": 0.0,
  "reason": "brief explanation"
}}
""".strip()

    def _parse_ollama_response(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1).replace("JSON\n", "", 1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(cleaned[start : end + 1])
            raise

    def compare_records(self, source_record: Dict[str, Any], target_record: Dict[str, Any]) -> LLMValidationResult:
        if not self.enabled:
            return self._offline_compare(source_record, target_record, "Ollama validation disabled in config.")

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": self._build_prompt(source_record, target_record),
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0},
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            parsed = self._parse_ollama_response(payload.get("response", "{}"))

            return LLMValidationResult(
                equivalent=bool(parsed.get("equivalent", False)),
                confidence=round(float(parsed.get("confidence", 0.0)), 4),
                reason=str(parsed.get("reason", "No reason provided.")),
                model=self.model,
                mode="ollama",
                provider="ollama-local",
            )
        except Exception as exc:  # noqa: BLE001
            return self._offline_compare(
                source_record,
                target_record,
                f"Ollama LLM call failed for model '{self.model}' at {self.base_url}. Error: {exc}",
            )

    @staticmethod
    def to_dict(result: LLMValidationResult) -> Dict[str, Any]:
        return asdict(result)
