from ..context import Context
from ..node import Node
from ..report import PipelineNodeReport
from .step_runner import StepRunner
from .middleware_engine import MiddlewareEngine


class NodeRunner:
  def __init__(
    self,
    middleware: MiddlewareEngine,
    steps: StepRunner,
  ):
    self.middleware = middleware
    self.steps = steps

  def run(
    self,
    ctx: Context,
    current_node: Node,
    node_report: PipelineNodeReport,
  ) -> bool:
    self.middleware.emit("beforeRunNode", ctx, node_report, current_node)

    prev_keys = set(ctx.data.keys())

    try:
      if not self.middleware.every(
        "validateInputs",
        ctx,
        current_node,
        node_report,
      ):
        return False

      if not self.steps.run(
        ctx,
        "onPreRun",
        current_node.onPreRun,
        current_node.onPreRunErr,
        node_report,
      ):
        return False

      if not self.steps.run(
        ctx,
        "onRun",
        current_node.onRun,
        current_node.onRunErr,
        node_report,
      ):
        return False

      if not self.steps.run(
        ctx,
        "onPostRun",
        current_node.onPostRun,
        current_node.onPostRunErr,
        node_report,
      ):
        return False

      if not self.middleware.every(
        "validateOutputs",
        ctx,
        current_node,
        node_report,
        prev_keys,
      ):
        return False

      return True

    finally:
      self.middleware.emit("afterRunNode", ctx, node_report, current_node)