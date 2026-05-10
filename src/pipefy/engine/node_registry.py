from typing import Self

from pipefy.node import Node
from pipefy.engine.middleware_engine import MiddlewareEngine

class NodeRegistry:
  def __init__(self, middleware: MiddlewareEngine):
    self.middleware = middleware
    self.nodes: list[Node] = []

  def push(self, n: Node) -> Self:
    self.nodes.append(
      self.middleware.emit_transform("onPush", n)
    )
    return self