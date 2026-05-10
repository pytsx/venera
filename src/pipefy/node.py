from abc import ABC, abstractmethod

from .pipeline import error

from .pipeline import context
from src.pipefy.sdk import reference

class Node(ABC):
  inputs: tuple[str, ...] = ()
  outputs: tuple[str, ...] = ()

  def __init__(self, id: str | None = None):
    self.id: str = id or reference.getReference(type(self))

  def onPreRun(self, ctx: context.Context) -> None:
    pass

  def onPreRunErr(
    self,
    ctx: context.ErrorContext,
  ) -> error.ErrorDecision:
    return  ctx.abort()

  @abstractmethod
  def onRun(self, ctx: context.Context) -> None:
    pass

  def onRunErr(
    self,
    ctx: context.ErrorContext,
  ) -> error.ErrorDecision:
    return  ctx.abort()

  def onPostRun(self, ctx: context.Context) -> None:
    pass

  def onPostRunErr(
    self,
    ctx: context.ErrorContext,
  ) -> error.ErrorDecision:
    return ctx.abort()