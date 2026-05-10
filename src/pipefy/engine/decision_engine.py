from typing import Callable

from pipefy.context import Context
from pipefy.error import ErrorDecision
from pipefy.report import report
from pipefy.engine.middleware_engine import MiddlewareEngine

class DecisionEngine:
  def __init__(self, middleware: MiddlewareEngine):
    self.middleware = middleware

  def finish_step(
    self,
    step_report: report.PipelineStepReport,
    node_report: report.PipelineNodeReport,
    success: bool,
    fixed: bool | None = None,
  ) -> bool:
    step_report.success = success
    step_report.fixed = fixed

    if not success:
      node_report.success = False

    node_report.steps.append(step_report)
    return success

  def handle(
    self,
    ctx: Context,
    action: Callable[[Context], None],
    decision: ErrorDecision,
    step_report: report.PipelineStepReport,
    node_report: report.PipelineNodeReport,
  ) -> bool:
    step_report.decision = decision.action
    step_report.decision_reason = decision.reason

    handlers = {
      "continue": self._continue,
      "skip": self._skip,
      "abort": self._abort,
      "retry": self._retry,
    }

    handler = handlers.get(decision.action)

    if handler is None:
      step_report.decision_reason = (
        step_report.decision_reason
        or f"Unknown error decision: {decision.action}"
      )
      return self.finish_step(step_report, node_report, False, False)

    return handler(ctx, action, decision, step_report, node_report)

  def _continue(self, ctx, action, decision, step_report, node_report):
    return self.finish_step(step_report, node_report, True, True)

  def _skip(self, ctx, action, decision, step_report, node_report):
    return self.finish_step(step_report, node_report, True, False)

  def _abort(self, ctx, action, decision, step_report, node_report):
    return self.finish_step(step_report, node_report, False, False)

  def _retry(self, ctx, action, decision, step_report, node_report):
    max_retries = decision.max_retries or 1

    for attempt in range(1, max_retries + 1):
      retry_report = report.PipelineRetryReport(
        attempt=attempt,
        success=True,
      )

      self.middleware.emit(
        "beforeRetry",
        ctx,
        retry_report,
        attempt,
        max_retries,
        action,
      )

      try:
        action(ctx)

        retry_report.success = True
        step_report.retries.append(retry_report)

        self.middleware.emit(
          "afterRetry",
          ctx,
          retry_report,
          attempt,
          max_retries,
          action,
        )

        return self.finish_step(step_report, node_report, True, True)

      except Exception as retry_err:
        retry_report.success = False

        self.middleware.emit(
          "onRetryError",
          ctx,
          retry_report,
          retry_err,
          attempt,
          max_retries,
          action,
        )

        step_report.retries.append(retry_report)

    return self.finish_step(step_report, node_report, False, False)