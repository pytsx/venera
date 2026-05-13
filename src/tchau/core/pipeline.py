from __future__ import annotations

from typing import Self

from .context import Context
from ..report.model import PipelineReport

from . import middleware
from ..middleware import (
  ReportTraceMiddleware,
  ValidationMiddleware,
  ErrorReportMiddleware,
  LoggerMiddleware,
)

from ..engine import (
 NodeRunner,
 ExecutionFrame,
 ExecutableRunner,
 ScopeRunner
)

from ..sdk import logger
from .scope import Scope
from .executable import Executable

class Pipeline(Scope):
  def __init__(self, log: logger.Logger, *mw: middleware.Middleware):
    self.log = log

    super().__init__(
      "root",
      middleware=[
        ReportTraceMiddleware(),
        ValidationMiddleware(),
        ErrorReportMiddleware(),
        LoggerMiddleware(),
        *mw
      ]
    )

    self.node_runner = NodeRunner()
    self.scope_runner = ScopeRunner()
    self.executable_runner = ExecutableRunner(self.node_runner, self.scope_runner)
    self.scope_runner.bind(self.executable_runner)

  def push(self, n: Executable) -> Self:
    self.children.append(n)
    return self

  def scope(
    self,
    name: str,
    *children: Executable,
    middleware: list[middleware.Middleware] | None = None,
  ) -> Self:
    return self.push(
      Scope(
        name,
        *children,
        middleware=middleware,
      )
    )

  def run(self) -> PipelineReport:
    ctx = Context(self.log)

    pipeline_report = PipelineReport(
      nodes_total=self._count_nodes(),
    )

    frame = ExecutionFrame(self.middlewares)
    middleware = frame.engine()
    middleware.emit("beforeRunPipeline", ctx, pipeline_report)

    try:
      for executable in self.children:
        if not self.executable_runner.run(ctx, frame, executable, pipeline_report):
          pipeline_report.success = False
          break

    finally:
      middleware.emit("afterRunPipeline", ctx, pipeline_report)

    return pipeline_report

  def _count_nodes(self) -> int:
    return sum(self._count_executable_nodes(child) for child in self.children)

  def _count_executable_nodes(self, executable: Executable) -> int:
    if isinstance(executable, Scope):
      return sum(
        self._count_executable_nodes(child)
        for child in executable.children
      )
    return 1