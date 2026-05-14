from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ErrorAction = Literal["abort", "retry", "recover"]

@dataclass
class ErrorDecision:
  action: ErrorAction
  reason: str | None = None
  max_retries: int = 0