
from typing import Self

from src.pipefy.context import Context
from src.pipefy.node import Node
from src.pipefy.report import report

from src.pipefy.middleware import middleware
from src.pipefy.middleware import (
  ReportTraceMiddleware,
  ValidationMiddleware,
  ErrorReportMiddleware,
  LoggerMiddleware,
)

from src.pipefy.engine import (
 NodeRunner,
 StepRunner,
 DecisionEngine,
 NodeRegistry,
 MiddlewareEngine,
)

from src.pipefy.sdk import logger

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
    self.decisions = DecisionEngine(self.middleware)
    self.steps = StepRunner(self.middleware, self.decisions)
    self.nodes = NodeRunner(self.middleware, self.steps)

  def push(self, n: Node) -> Self:
    self.registry.push(n)
    return self

  def run(self) -> report.PipelineReport:
    ctx = Context(self.log)

    pipeline_report = report.PipelineReport(
      nodes_total=len(self.registry.nodes),
    )

    self.middleware.emit("beforeRunPipeline", ctx, pipeline_report)

    for current_node in self.registry.nodes:
      node_report = report.PipelineNodeReport(node_id=current_node.id)
      pipeline_report.nodes.append(node_report)

      if not self.nodes.run(ctx, current_node, node_report):
        pipeline_report.success = False
        break

    self.middleware.emit("afterRunPipeline", ctx, pipeline_report)

    return pipeline_report