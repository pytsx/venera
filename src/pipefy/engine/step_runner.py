from typing import Callable

from src.pipefy.context import Context, ErrorContext
from src.pipefy.error import ErrorDecision
from src.pipefy.report import report
from src.pipefy.engine.decision_engine import DecisionEngine
from src.pipefy.engine.middleware_engine import MiddlewareEngine
from src.pipefy.sdk import reference


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
    node_report: report.PipelineNodeReport,
  ) -> bool:
    step_report = report.PipelineStepReport(
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