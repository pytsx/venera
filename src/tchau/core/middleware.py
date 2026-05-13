from abc import ABC
from typing import Callable, Literal

from .context import Context
from .node import Node
from ..report.model import  PipelineNodeReport, PipelineReport, PipelineRetryReport, PipelineStepReport

MiddlewareEvent = Literal[
  "onPush",
  "beforeRunPipeline",
  "afterRunPipeline",
  "beforeRunNode",
  "afterRunNode",
  "beforeRunStep",
  "afterRunStep",
  "onStepError",
  "validateInputs",
  "validateOutputs",
  "beforeRetry",
  "afterRetry",
  "onRetryError",
]

class Middleware(ABC):
  events: tuple[MiddlewareEvent, ...] = (
    "onPush",
    "beforeRunPipeline",
    "afterRunPipeline",
    "beforeRunNode",
    "afterRunNode",
    "beforeRunStep",
    "afterRunStep",
    "onStepError",
    "validateInputs",
    "validateOutputs",
    "beforeRetry",
    "afterRetry",
    "onRetryError",
  )

  def listens(self, event: MiddlewareEvent) -> bool:
    return event in self.events

  def onPush(self, n: Node) -> Node:
    return n

  def beforeRunPipeline(self, ctx: Context, r: PipelineReport) -> None:
    pass

  def afterRunPipeline(self, ctx: Context, r: PipelineReport) -> None:
    pass

  def beforeRunNode(self, ctx: Context, r: PipelineNodeReport, n: Node) -> None:
    pass

  def afterRunNode(self, ctx: Context, r: PipelineNodeReport, n: Node) -> None:
    pass

  def beforeRunStep(self, ctx: Context, r: PipelineStepReport, name: str, action: Callable) -> None:
    pass

  def afterRunStep(self, ctx: Context, r: PipelineStepReport, name: str, action: Callable) -> None:
    pass

  def onStepError(self, ctx: Context, r: PipelineStepReport, err: Exception, error_handler: Callable) -> None:
    pass

  def validateInputs(self, ctx: Context, n: Node, r: PipelineNodeReport) -> bool:
    return True

  def validateOutputs(self, ctx: Context, n: Node, r: PipelineNodeReport, prev_keys: set[str]) -> bool:
    return True

  def beforeRetry(self, ctx: Context, r: PipelineRetryReport, attempt: int, max_retries: int, action: Callable) -> None:
    pass

  def afterRetry(self, ctx: Context, r: PipelineRetryReport, attempt: int, max_retries: int, action: Callable) -> None:
    pass

  def onRetryError(self, ctx: Context, r: PipelineRetryReport, err: Exception, attempt: int, max_retries: int, action: Callable) -> None:
    pass

