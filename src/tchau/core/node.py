from abc import abstractmethod

from .error import ErrorDecision

from .context import Context, ErrorContext
from .executable import Executable

from .source import SourceKey

from typing import ClassVar, Any

class Node[I, O](Executable[I, O]):
  source: ClassVar[SourceKey[Any] | None] = None

  def __init__(self, id: str | None = None):
    super().__init__(id)

  def before(self, ctx: Context) -> None:
    pass

  def beforeErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return ctx.abort()

  @abstractmethod
  def run(self, ctx: Context, value: I) -> O:
    pass

  def runErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return  ctx.abort()

  def after(self, ctx: Context) -> None:
    pass

  def afterErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return ctx.abort()
  
  def close(self, ctx: Context) -> None:
    pass

  def closeErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return ctx.abort()
  
class InternalNode:
  def __init__(self, node: Node):
    self.node = node 

  def has_before(self) -> bool:
    return type(self.node).before is not Node.before

  def has_after(self) -> bool:
    return type(self.node).after is not Node.after
  
  def has_close(self) -> bool:
    return type(self.node).close is not Node.close
  
  def has_source(self) -> bool:
    return self.node.source is not None