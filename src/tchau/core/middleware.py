from __future__ import annotations

import inspect
from abc import ABC
from typing import Callable, TYPE_CHECKING, TypeAlias

from .context import Context
from .node import Node
from ..report.model import (
  PipelineNodeReport,
  PipelineReport,
  PipelineRetryReport,
  PipelineStepReport,
)

if TYPE_CHECKING:
  from .scope import Scope

MiddlewareEvent: TypeAlias = str

class Middleware(ABC):
  @classmethod
  def hook_names(cls) -> list[str]:
    ignored = {
      "events",
      "listens",
      "hook_names",
    }

    hooks: list[str] = []

    for name, value in inspect.getmembers(Middleware, predicate=inspect.isfunction):
      if name.startswith("_"):
        continue

      if name in ignored:
        continue

      hooks.append(name)

    return hooks

  def events(self) -> list[str]:
    implemented: list[str] = []
    middleware_type = type(self)

    for name in self.hook_names():
      base_impl = inspect.getattr_static(Middleware, name)
      current_impl = inspect.getattr_static(middleware_type, name, None)

      if current_impl is not base_impl:
        implemented.append(name)

    return implemented

  def listens(self, event: MiddlewareEvent) -> bool:
    return event in self.events()

  def onPush(self, n: Node) -> Node:
    return n

  def beforeRunPipeline(self, ctx: Context, r: PipelineReport) -> None:
    pass

  def afterRunPipeline(self, ctx: Context, r: PipelineReport) -> None:
    pass

  def beforeRunScope(self, ctx: Context, r: PipelineReport, scope: Scope) -> None:
    pass

  def afterRunScope(self, ctx: Context, r: PipelineReport, scope: Scope) -> None:
    pass

  def beforeRunNode(self, ctx: Context, r: PipelineNodeReport, n: Node) -> None:
    pass

  def afterRunNode(self, ctx: Context, r: PipelineNodeReport, n: Node) -> None:
    pass

  def beforeRunStep(
    self,
    ctx: Context,
    r: PipelineStepReport,
    name: str,
    action: Callable,
  ) -> None:
    pass

  def afterRunStep(
    self,
    ctx: Context,
    r: PipelineStepReport,
    name: str,
    action: Callable,
  ) -> None:
    pass

  def onStepError(
    self,
    ctx: Context,
    r: PipelineStepReport,
    err: Exception,
    error_handler: Callable,
  ) -> None:
    pass

  def validateInputs(
    self,
    ctx: Context,
    n: Node,
    r: PipelineNodeReport,
  ) -> bool:
    return True

  def validateOutputs(
    self,
    ctx: Context,
    n: Node,
    r: PipelineNodeReport,
    prev_keys: set[str],
  ) -> bool:
    return True

  def beforeRetry(
    self,
    ctx: Context,
    r: PipelineRetryReport,
    attempt: int,
    max_retries: int,
    action: Callable,
  ) -> None:
    pass

  def afterRetry(
    self,
    ctx: Context,
    r: PipelineRetryReport,
    attempt: int,
    max_retries: int,
    action: Callable,
  ) -> None:
    pass

  def onRetryError(
    self,
    ctx: Context,
    r: PipelineRetryReport,
    err: Exception,
    attempt: int,
    max_retries: int,
    action: Callable,
  ) -> None:
    pass