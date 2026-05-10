import logging

import pytest

from .context import Context, ErrorContext
from .node import Node
from .pipeline import Pipeline
from .error import ErrorDecision

from .sdk import logger


class NoopLogger(logger.Logger):
  def __init__(self):
    self.messages = []

  def info(self, ref: str, *msg):
    self.messages.append(("info", ref, msg))

  def error(self, ref: str, *msg):
    self.messages.append(("error", ref, msg))

  def warn(self, ref: str, *msg):
    self.messages.append(("warn", ref, msg))

  def warning(self, ref: str, *msg):
    self.warn(ref, *msg)

  def critical(self, ref: str, *msg):
    self.messages.append(("critical", ref, msg))

  def debug(self, ref: str, *msg):
    self.messages.append(("debug", ref, msg))


class Extract(Node):
  outputs = ("text",)

  def onRun(self, ctx: Context):
    ctx.set("text", {"message": "hello"})


class Upload(Node):
  inputs = ("text",)
  outputs = ("uploaded",)

  def onRun(self, ctx: Context):
    payload = ctx.get("text")
    ctx.set("uploaded", payload["message"] == "hello")


class MissingInputNode(Node):
  inputs = ("missing",)

  def onRun(self, ctx: Context):
    pass


class RecoverableError(Exception):
  pass


class RecoverableNode(Node):
  outputs = ("recovered",)

  def onRun(self, ctx: Context):
    ctx.set("recovered", True)
    raise RecoverableError("erro recuperavel")

  def onRunErr(self, ctx: ErrorContext) -> ErrorDecision:
    if ctx.is_(RecoverableError):
      return ctx.continue_("erro esperado tratado")
    return ctx.abort()


def make_pipeline(*nodes: Node):
  p = Pipeline(NoopLogger())
  for n in nodes:
    p.push(n)
  return p


def test_pipeline_success_with_declared_inputs_and_outputs():
  result = make_pipeline(Extract(), Upload()).run()

  assert result.success is True
  assert result.nodes_total == 2
  assert result.nodes_success == 2
  assert result.nodes_failed == 0
  assert len(result.nodes) == 2

  extract_report, upload_report = result.nodes
  assert extract_report.success is True
  assert upload_report.success is True
  assert extract_report.outputs_declared == ["text"]
  assert upload_report.inputs_declared == ["text"]
  assert upload_report.outputs_declared == ["uploaded"]

  report_dict = result.to_dict()
  assert report_dict["success"] is True
  assert report_dict["nodes_total"] == 2


def test_pipeline_fails_when_input_is_missing():
  result = make_pipeline(MissingInputNode()).run()

  assert result.success is False
  assert result.nodes_total == 1
  assert result.nodes_success == 0
  assert result.nodes_failed == 1
  assert result.failed_node is not None
  assert result.failed_node.missing_inputs == ["missing"]


def test_pipeline_can_continue_after_handled_error():
  result = make_pipeline(RecoverableNode()).run()

  assert result.success is True
  assert result.nodes_total == 1
  assert result.nodes_success == 1
  assert result.nodes_failed == 0

  run_step = next(step for step in result.nodes[0].steps if step.name == "onRun")
  assert run_step.success is True
  assert run_step.decision == "continue"
  assert run_step.fixed is True
  assert run_step.error is not None
  assert run_step.error.type == "RecoverableError"


def test_report_can_be_rendered_to_html():
  result = make_pipeline(Extract(), Upload()).run()
  html = result.to_html()

  assert "Pipeline Report" in html
  assert "Node:" in html
  assert "Sucesso" in html
