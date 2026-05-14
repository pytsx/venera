from typing import Any

from ..core.middleware import Middleware
from ..core.node import Node


class ValidationMiddleware(Middleware):
  def beforeRunNode(self, ctx, r, n: Node[Any, Any]):
    ctx.begin_tracking()

  def validateInputs(self, ctx, n: Node[Any, Any], r) -> bool:
    source = getattr(n, "source", None)

    if source is not None and not ctx.has_source(source):
      ctx.log.info(n.id, f"missing source: {source.name}")
      r.success = False
      r.missing_inputs.append(f"source:{source.name}")
      return False

    return True
