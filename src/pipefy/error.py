from dataclasses import dataclass
from typing import Literal

ErrorAction = Literal["abort", "retry", "skip", "continue"]

@dataclass
class ErrorDecision:
  action: ErrorAction 
  reason: str | None = None 
  max_retries: int = 0