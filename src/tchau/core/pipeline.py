from __future__ import annotations

from typing import Any, Self

from .context import Context
from .executable import Executable
from .scope import Scope
from .source import Source

from ..report.model import PipelineReport

from . import middleware as _mid
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
  ScopeRunner,
)

from ..sdk import logger


class Pipeline(Scope[None, Any]):
  def __init__(
    self,
    log: logger.Logger,
    *children: Executable[Any, Any],
    middleware: list[_mid.Middleware] | None = None,
    sources: list[Source[Any]] | None = None,
  ):
    self.log = log

    super().__init__(
      "root",
      *children,
      middleware=[
        ReportTraceMiddleware(),
        ValidationMiddleware(),
        ErrorReportMiddleware(),
        LoggerMiddleware(),
        *(middleware or []),
      ],
      sources=sources,
    )

    self.node_runner = NodeRunner()
    self.scope_runner = ScopeRunner()
    self.executable_runner = ExecutableRunner(
      self.node_runner,
      self.scope_runner,
    )
    self.scope_runner.bind(self.executable_runner)

  def push(self, n: Executable[Any, Any]) -> Self:
    self.children.append(n)
    self._infer_types_from_children()
    return self

  def scope(
    self,
    name: str,
    *children: Executable[Any, Any],
    middleware: list[_mid.Middleware] | None = None,
    sources: list[Source[Any]] | None = None,
  ) -> Self:
    return self.push(
      Scope(
        name,
        *children,
        middleware=middleware,
        sources=sources,
      )
    )

  def run(self) -> PipelineReport:
    ctx = Context(self.log)

    pipeline_report = PipelineReport(
      nodes_total=self._count_nodes(),
    )

    root_frame = ExecutionFrame([])
    engine = ExecutionFrame(self.middlewares).engine()

    engine.emit("beforeRunPipeline", ctx, pipeline_report)

    try:
      result = self.scope_runner.run(
        ctx,
        root_frame,
        self,
        pipeline_report,
        None,
      )

      if not result.success:
        pipeline_report.success = False

    finally:
      engine.emit("afterRunPipeline", ctx, pipeline_report)

    return pipeline_report

  def _count_nodes(self) -> int:
    return sum(
      self._count_executable_nodes(child)
      for child in self.children
    )

  def _count_executable_nodes(
    self,
    executable: Executable[Any, Any],
  ) -> int:
    if isinstance(executable, Scope):
      return sum(
        self._count_executable_nodes(child)
        for child in executable.children
      )

    return 1