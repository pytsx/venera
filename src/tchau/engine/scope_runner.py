from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ..core.context import Context
from ..core.result import RunResult
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
    frame: ExecutionFrame,
    scope: Scope[Any, Any],
    report: PipelineReport,
    payload: Any,
  ) -> RunResult[Any]:
    if self.executables is None:
      raise RuntimeError("ScopeRunner is not bound to ExecutableRunner")

    scope_frame = frame.child(scope.middlewares)
    middleware = scope_frame.engine()

    opened: list[tuple[Any, Any]] = []
    current_payload = payload

    middleware.emit("beforeRunScope", ctx, report, scope)
    ctx.push_source_scope()

    try:
      for source in scope.sources:
        try:
          resource = source.open(ctx)
          ctx.register_source(source.key, resource)
          opened.append((source, resource))

        except Exception as err:
          ctx.log.error(
            source.key.name,
            "source open failed",
            err,
          )
          return RunResult(False)

      for child in scope.children:
        result = self.executables.run(
          ctx,
          scope_frame,
          child,
          report,
          current_payload,
        )

        if not result.success:
          return RunResult(False)

        current_payload = result.payload

      return RunResult(True, current_payload)

    finally:
      for source, resource in reversed(opened):
        try:
          source.close(ctx, resource)
        except Exception as err:
          ctx.log.error(source.key.name, "source close failed", err)

          if source.close_errors_are_fatal:
            raise

      ctx.pop_source_scope()
      middleware.emit("afterRunScope", ctx, report, scope)