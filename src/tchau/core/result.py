from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class RunResult(Generic[T]):
  success: bool
  payload: T | None = None