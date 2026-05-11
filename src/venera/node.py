from abc import ABC, abstractmethod

from .error import ErrorDecision

from .context import Context, ErrorContext
from .sdk import reference

class Node(ABC):
  inputs: tuple[str, ...] = ()
  outputs: tuple[str, ...] = ()

  def __init__(self, id: str | None = None):
    self.id: str = id or reference.getReference(type(self))

  def onPreRun(self, ctx: Context) -> None:
    pass

  def onPreRunErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return  ctx.abort()

  @abstractmethod
  def onRun(self, ctx: Context) -> None:
    pass

  def onRunErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return  ctx.abort()

  def onPostRun(self, ctx: Context) -> None:
    pass

  def onPostRunErr(
    self,
    ctx: ErrorContext,
  ) -> ErrorDecision:
    return ctx.abort()