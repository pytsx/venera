from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class RunResult(Generic[T]):
  success: bool
  payload: T | None = None

  # True quando a execução continuou por recuperação de erro.
  # Nesse caso o payload não foi produzido pela action original;
  # normalmente ele é o payload anterior preservado.
  recovered: bool = False