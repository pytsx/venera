from typing import Any

from ..core.middleware import Middleware
from ..core.node import Node

class ValidationMiddleware(Middleware):
  def beforeRunNode(self, ctx, r, n: Node[Any, Any]):
    ctx.begin_tracking()

  def validateInputs(self, ctx, n: Node[Any, Any], r) -> bool:
    return True