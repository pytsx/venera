from __future__ import annotations

from typing import Any, Callable, TypeVar

from ..core.context import Context
from ..core.error import ErrorDecision
from ..core.result import RunResult
from ..report.model import (
  PipelineNodeReport,
  PipelineRetryReport,
  PipelineStepReport,
)
from ..engine.middleware_engine import MiddlewareEngine

T = TypeVar("T")


class DecisionEngine:
  def __init__(self, middleware: MiddlewareEngine):
    self.middleware = middleware

  def finish_step(
    self,
    step_report: PipelineStepReport,
    node_report: PipelineNodeReport,
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
    action: Callable[[], T],
    decision: ErrorDecision,
    step_report: PipelineStepReport,
    node_report: PipelineNodeReport,
  ) -> RunResult[T]:
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
      self.finish_step(step_report, node_report, False, False)
      return RunResult(False)

    return handler(ctx, action, decision, step_report, node_report)

  def _continue(
    self,
    ctx: Context,
    action: Callable[[], T],
    decision: ErrorDecision,
    step_report: PipelineStepReport,
    node_report: PipelineNodeReport,
  ) -> RunResult[T]:
    self.finish_step(step_report, node_report, True, True)
    return RunResult(True)

  def _skip(
    self,
    ctx: Context,
    action: Callable[[], T],
    decision: ErrorDecision,
    step_report: PipelineStepReport,
    node_report: PipelineNodeReport,
  ) -> RunResult[T]:
    self.finish_step(step_report, node_report, True, False)
    return RunResult(True)

  def _abort(
    self,
    ctx: Context,
    action: Callable[[], T],
    decision: ErrorDecision,
    step_report: PipelineStepReport,
    node_report: PipelineNodeReport,
  ) -> RunResult[T]:
    self.finish_step(step_report, node_report, False, False)
    return RunResult(False)

  def _retry(
    self,
    ctx: Context,
    action: Callable[[], T],
    decision: ErrorDecision,
    step_report: PipelineStepReport,
    node_report: PipelineNodeReport,
  ) -> RunResult[T]:
    max_retries = decision.max_retries or 1

    for attempt in range(1, max_retries + 1):
      retry_report = PipelineRetryReport(
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
        value = action()

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

        self.finish_step(step_report, node_report, True, True)
        return RunResult(True, value)

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

    self.finish_step(step_report, node_report, False, False)
    return RunResult(False)