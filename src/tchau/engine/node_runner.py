from __future__ import annotations

from typing import Any, get_args, get_origin

from ..core.context import Context
from ..core.node import InternalNode, Node
from ..core.result import RunResult
from ..report.model import PipelineNodeReport

from .decision_engine import DecisionEngine
from .execution_frame import ExecutionFrame
from .step_runner import StepRunner


class NodeRunner:
  def run(
    self,
    ctx: Context,
    framer: ExecutionFrame,
    current_node: Node[Any, Any],
    node_report: PipelineNodeReport,
    payload: Any,
  ) -> RunResult[Any]:

    engine = framer.engine()
    steps = StepRunner(engine, DecisionEngine(engine))

    engine.emit("beforeRunNode", ctx, node_report, current_node)

    _node = InternalNode(current_node)

    try:
      if not self._validate_input(ctx, current_node, node_report, payload):
        return RunResult(False)

      if not engine.every(
        "validateInputs",
        ctx,
        current_node,
        node_report,
      ):
        return RunResult(False)

      output: Any = payload
      close_ok = True

      try:
        if _node.has_before():
          before = steps.run(
            ctx,
            "before",
            lambda: current_node.before(ctx),
            current_node.beforeErr,
            node_report,
            previous_payload=payload,
          )

          if not before.success:
            return RunResult(False)

        run = steps.run(
          ctx,
          "run",
          lambda: current_node.run(ctx, payload),
          current_node.runErr,
          node_report,
          previous_payload=payload,
        )

        if not run.success:
          return RunResult(False)

        output = run.payload

        if not self._validate_output(ctx, current_node, node_report, output):
          return RunResult(False)

        if _node.has_after():
          after = steps.run(
            ctx,
            "after",
            lambda: current_node.after(ctx),
            current_node.afterErr,
            node_report,
            previous_payload=output,
          )

          if not after.success:
            return RunResult(False)

      finally:
        if _node.has_close():
          close = steps.run(
            ctx,
            "close",
            lambda: current_node.close(ctx),
            current_node.closeErr,
            node_report,
            previous_payload=output,
          )

          close_ok = close.success

      if not close_ok:
        return RunResult(False)

      if not engine.every(
        "validateOutputs",
        ctx,
        current_node,
        node_report,
        set(ctx.data.keys()),
      ):
        return RunResult(False)

      return RunResult(True, output)

    finally:
      engine.emit("afterRunNode", ctx, node_report, current_node)

  def _validate_input(
    self,
    ctx: Context,
    node: Node[Any, Any],
    node_report: PipelineNodeReport,
    value: Any,
  ) -> bool:
    expected = getattr(node, "__input_type__", Any)

    if self._matches(expected, value):
      return True

    node_report.success = False
    ctx.log.info(
      node.id,
      f"invalid input type: expected {self._type_name(expected)}, got {type(value).__name__}",
    )
    return False

  def _validate_output(
    self,
    ctx: Context,
    node: Node[Any, Any],
    node_report: PipelineNodeReport,
    value: Any,
  ) -> bool:
    expected = getattr(node, "__output_type__", Any)

    if self._matches(expected, value):
      return True

    node_report.success = False
    ctx.log.info(
      node.id,
      f"invalid output type: expected {self._type_name(expected)}, got {type(value).__name__}",
    )
    return False

  def _matches(self, expected: Any, value: Any) -> bool:
    if expected is Any:
      return True

    if expected is None or expected is type(None):
      return value is None

    if isinstance(expected, type):
      return isinstance(value, expected)

    origin = get_origin(expected)

    if origin is list:
      if not isinstance(value, list):
        return False

      args = get_args(expected)

      if not args:
        return True

      return all(isinstance(item, args[0]) for item in value)

    if origin is dict:
      return isinstance(value, dict)

    if isinstance(origin, type):
      return isinstance(value, origin)

    return True

  def _type_name(self, value: Any) -> str:
    if value is Any:
      return "Any"

    if value is None or value is type(None):
      return "None"

    return getattr(value, "__name__", str(value))