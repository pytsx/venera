from __future__ import annotations

from typing import Any, NoReturn, Protocol

from ..core.context import Context
from ..core.executable import Executable
from ..core.node import Node
from ..core.result import RunResult
from ..core.scope import Scope

from ..report.model import PipelineNodeReport, PipelineReport

from .execution_frame import ExecutionFrame
from .node_runner import NodeRunner


class ScopeRunnerProtocol(Protocol):
  def run(
    self,
    ctx: Context,
    frame: ExecutionFrame,
    scope: Scope[Any, Any],
    report: PipelineReport,
    payload: Any,
  ) -> RunResult[Any]:
    ...


class ExecutableRunner:
  def __init__(
    self,
    nodes: NodeRunner,
    scopes: ScopeRunnerProtocol,
  ) -> None:
    self.nodes = nodes
    self.scopes = scopes

  def run(
    self,
    ctx: Context,
    frame: ExecutionFrame,
    executable: Executable[Any, Any],
    report: PipelineReport,
    payload: Any,
  ) -> RunResult[Any]:
    if isinstance(executable, Node):
      node_report = PipelineNodeReport(node_id=executable.id)
      report.nodes.append(node_report)

      return self.nodes.run(
        ctx,
        frame,
        executable,
        node_report,
        payload,
      )

    if isinstance(executable, Scope):
      return self.scopes.run(
        ctx,
        frame,
        executable,
        report,
        payload,
      )

    return self.unsupported(executable)

  def unsupported(self, executable: Executable[Any, Any]) -> NoReturn:
    raise TypeError(
      f"Unsupported executable: {type(executable).__name__}"
    )