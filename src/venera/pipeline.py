
from typing import Self

from .context import Context
from .node import Node
from .report import PipelineNodeReport, PipelineReport

from .middleware import middleware
from .middleware import (
  ReportTraceMiddleware,
  ValidationMiddleware,
  ErrorReportMiddleware,
  LoggerMiddleware,
)

from .engine import (
 NodeRunner,
 StepRunner,
 DecisionEngine,
 NodeRegistry,
 MiddlewareEngine,
)

from .sdk import logger

class Pipeline:
  def __init__(self, log: logger.Logger, *mw: middleware.Middleware):
    self.log = log

    self.middleware = MiddlewareEngine(
      ReportTraceMiddleware(),
      ValidationMiddleware(),
      ErrorReportMiddleware(),
      LoggerMiddleware(),
      *mw,
    )

    self.registry = NodeRegistry(self.middleware)
    self.nodes = NodeRunner(
      self.middleware, 
      StepRunner(self.middleware, 
        DecisionEngine(self.middleware)
      )
    )

  def push(self, n: Node) -> Self:
    self.registry.push(n)
    return self

  def run(self) -> PipelineReport:
    ctx = Context(self.log)

    pipeline_report = PipelineReport(
      nodes_total=len(self.registry.nodes),
    )

    self.middleware.emit("beforeRunPipeline", ctx, pipeline_report)

    for current_node in self.registry.nodes:
      node_report = PipelineNodeReport(node_id=current_node.id)
      pipeline_report.nodes.append(node_report)

      if not self.nodes.run(ctx, current_node, node_report):
        pipeline_report.success = False
        break

    self.middleware.emit("afterRunPipeline", ctx, pipeline_report)

    return pipeline_report