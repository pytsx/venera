from .executable import Executable 
from ..middleware import Middleware

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