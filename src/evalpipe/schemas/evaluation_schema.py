from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime, timezone


@dataclass
class ProviderOutput:
    output: str
    model: str
    latency_ms: int
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]


@dataclass
class EvaluationResult:
    schema_version: str
    run_id: str
    provider: str
    prompt: str
    provider_output: ProviderOutput
    metrics: Dict[str, Any]
    timestamp: str

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
