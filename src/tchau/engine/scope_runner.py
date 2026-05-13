from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.context import Context
from ..core.scope import Scope
from ..report.model import PipelineReport

from .execution_frame import ExecutionFrame

if TYPE_CHECKING:
  from .executable_runner import ExecutableRunner


class ScopeRunner:
  def __init__(
    self,
    executables: ExecutableRunner | None = None,
  ) -> None:
    self.executables = executables

  def bind(self, executables: ExecutableRunner) -> "ScopeRunner":
    self.executables = executables
    return self

  def run(
    self,
    ctx: Context,
    frame:ExecutionFrame,
    scope: Scope,
    report: PipelineReport,
  ) -> bool:
    if self.executables is None:
      raise RuntimeError("ScopeRunner is not bound to ExecutableRunner")

    scope_frame = frame.child(scope.middlewares)
    middleware = scope_frame.engine()

    ok = True

    try:
      middleware.emit("beforeRunScope", ctx, report, scope)

      for child in scope.children:
        if not self.executables.run(ctx, scope_frame, child, report):
          ok = False
          return False

      return True

    finally:
      middleware.emit("afterRunScope", ctx, report, scope)