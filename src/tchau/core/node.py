from __future__ import annotations

from abc import abstractmethod
from typing import Any, ClassVar

from .context import Context, ErrorContext
from .error import ErrorDecision
from .executable import Executable
from .source import SourceKey


class Node[I, O](Executable[I, O]):
  source: ClassVar[SourceKey[Any] | None] = None

  def __init__(self, id: str | None = None):
    super().__init__(id)

  @abstractmethod
  def run(self, ctx: Context, value: I) -> O:
    pass

  def on_error(self, ctx: ErrorContext) -> ErrorDecision:
    return ctx.abort()


class InternalNode:
  def __init__(self, node: Node):
    self.node = node

  def has_source(self) -> bool:
    return self.node.source is not None