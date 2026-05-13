from typing import Callable

from ..core.context import Context, ErrorContext
from ..core.error import ErrorDecision
from ..report.model import PipelineNodeReport, PipelineStepReport
from ..sdk import reference

from .decision_engine import DecisionEngine
from .middleware_engine import MiddlewareEngine

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
    action: Callable[[Context], None],
    error_handler: Callable[[ErrorContext], ErrorDecision],
    node_report: PipelineNodeReport,
  ) -> bool:
    step_report = PipelineStepReport(
      name=name,
      reference=reference.getReference(action),
      success=True,
    )

    self.middleware.emit("beforeRunStep", ctx, step_report, name, action)

    try:
      action(ctx)

      result = self.decisions.finish_step(
        step_report,
        node_report,
        True,
      )

      self.middleware.emit("afterRunStep", ctx, step_report, name, action)
      return result

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

        result = self.decisions.finish_step(
          step_report,
          node_report,
          False,
          False,
        )

        self.middleware.emit("afterRunStep", ctx, step_report, name, action)
        return result

      result = self.decisions.handle(
        ctx=ctx,
        action=action,
        decision=decision,
        step_report=step_report,
        node_report=node_report,
      )

      self.middleware.emit("afterRunStep", ctx, step_report, name, action)
      return result