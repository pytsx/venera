from __future__ import annotations

from typing import TYPE_CHECKING

from .executable import Executable 

if TYPE_CHECKING:
  from .middleware import Middleware


class Scope(Executable):
  def __init__(
    self,
    name: str,
    *children: Executable,
    middleware: list[Middleware] | None = None,
  ):
    super().__init__(name)
    self.name = name
    self.children = list(children)
    self.middlewares = middleware or []