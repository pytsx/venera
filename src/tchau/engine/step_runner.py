from __future__ import annotations

from typing import Any, Callable, TypeVar

from ..core.context import Context, ErrorContext
from ..core.error import ErrorDecision
from ..core.result import RunResult
from ..report.model import PipelineNodeReport, PipelineStepReport
from ..sdk import reference

from .decision_engine import DecisionEngine
from .middleware_engine import MiddlewareEngine

T = TypeVar("T")


class StepRunner:
  def __init__(
    self,
    middleware: MiddlewareEngine,
    decisions: DecisionEngine,
  ):
    self.middleware = middleware
    self.decisions = decisions

  def run(
    self,
    ctx: Context,
    name: str,
    action: Callable[[], T],
    error_handler: Callable[[ErrorContext], ErrorDecision],
    node_report: PipelineNodeReport,
    previous_payload: Any = None,
  ) -> RunResult[T]:
    step_report = PipelineStepReport(
      name=name,
      reference=reference.getReference(action),
      success=True,
    )

    self.middleware.emit("beforeRunStep", ctx, step_report, name, action)

    try:
      value = action()

      self.decisions.finish_step(
        step_report,
        node_report,
        True,
      )

      self.middleware.emit("afterRunStep", ctx, step_report, name, action)
      return RunResult(True, value)

    except Exception as err:
      err_ctx = ErrorContext(ctx, err)

      self.middleware.emit("onStepError", ctx, step_report, err, error_handler)

      try:
        decision = error_handler(err_ctx)

        if decision is None:
          decision = err_ctx.abort(f"{name} must return an ErrorDecision")

      except Exception as handler_err:
        self.middleware.emit(
          "onStepError",
          ctx,
          step_report,
          handler_err,
          error_handler,
        )

        step_report.decision = "abort"
        step_report.decision_reason = "error handler failed"

        self.decisions.finish_step(
          step_report,
          node_report,
          False,
          False,
        )

        self.middleware.emit("afterRunStep", ctx, step_report, name, action)
        return RunResult(False)

      result = self.decisions.handle(
        ctx=ctx,
        action=action,
        decision=decision,
        step_report=step_report,
        node_report=node_report,
        previous_payload=previous_payload,
      )

      self.middleware.emit("afterRunStep", ctx, step_report, name, action)
      return result