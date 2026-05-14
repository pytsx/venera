from __future__ import annotations

from typing import Any, get_args, get_origin

from ..core.context import Context
from ..core.node import Node
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
    prev_keys = set(ctx.data.keys())

    engine.emit("beforeRunNode", ctx, node_report, current_node)

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

      run = steps.run(
        ctx,
        "run",
        lambda: current_node.run(ctx, payload),
        current_node.on_error,
        node_report,
        previous_payload=payload,
      )

      if not run.success:
        return RunResult(False)

      output = run.payload

      # Quando o node recupera de erro, ele não produziu uma saída real.
      # O payload anterior é preservado e a validação do output declarado
      # deste node é ignorada para não invalidar uma recuperação legítima.
      if not run.recovered:
        if not self._validate_output(ctx, current_node, node_report, output):
          return RunResult(False)

      if not engine.every(
        "validateOutputs",
        ctx,
        current_node,
        node_report,
        prev_keys,
      ):
        return RunResult(False)

      return RunResult(True, output, recovered=run.recovered)

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

      item_type = args[0]

      if item_type is Any:
        return True

      if not isinstance(item_type, type):
        return True

      return all(isinstance(item, item_type) for item in value)

    if origin is dict:
      return isinstance(value, dict)

    if origin is tuple:
      return isinstance(value, tuple)

    if origin is set:
      return isinstance(value, set)

    if isinstance(origin, type):
      return isinstance(value, origin)

    return True

  def _type_name(self, value: Any) -> str:
    if value is Any:
      return "Any"

    if value is None or value is type(None):
      return "None"

    return getattr(value, "__name__", str(value))