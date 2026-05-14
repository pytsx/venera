from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .executable import Executable
from .source import Source

if TYPE_CHECKING:
  from .middleware import Middleware


class Scope[I, O](Executable[I, O]):
  def __init__(
    self,
    name: str,
    *children: Executable[Any, Any],
    middleware: list[Middleware] | None = None,
    sources: list[Source[Any]] | None = None,
  ):
    super().__init__(name)
    self.name = name
    self.children: list[Executable[Any, Any]] = list(children)
    self.middlewares = middleware or []
    self.sources = sources or []

    self._infer_types_from_children()

  def _infer_types_from_children(self) -> None:
    if not self.children:
      return

    first = self.children[0]
    last = self.children[-1]

    self.__input_type__ = getattr(first, "__input_type__", Any)
    self.__output_type__ = getattr(last, "__output_type__", Any)