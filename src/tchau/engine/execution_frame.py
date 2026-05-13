from __future__ import annotations

from typing import  Self

from ..core.context import Context
from ..core.scope import Scope
from ..core.middleware import Middleware

from ..engine.middleware_engine import MiddlewareEngine

from ..report.model import PipelineReport


class ExecutionFrame:
  def __init__(self, mw: list[Middleware]):
    self.middlewares = mw 

  def child(self, extra: list[Middleware]) -> Self:
    return ExecutionFrame([
      *self.middlewares,
      *extra
    ])  

  def engine(self) -> MiddlewareEngine:
    return MiddlewareEngine(*self.middlewares)
