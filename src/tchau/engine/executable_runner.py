from __future__ import annotations

from typing import NoReturn, Self

from ..core.context import Context
from ..core.executable import Executable
from ..core.node import Node
from ..core.scope import Scope

from ..report.model import PipelineNodeReport, PipelineReport

from .execution_frame import ExecutionFrame
from .node_runner import NodeRunner
from .execution_frame import ExecutionFrame

class ScopeRunnerProtocol:
  def run(
    self,
    ctx: Context,
    scope: Scope,
    report: PipelineReport,
  ) -> bool:
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
    frame:ExecutionFrame,
    executable: Executable,
    report: PipelineReport,
  ) -> bool:
    if isinstance(executable, Node):
      node_report = PipelineNodeReport(node_id=executable.id)
      report.nodes.append(node_report)
      return self.nodes.run(ctx, frame, executable, node_report)

    if isinstance(executable, Scope):
      return self.scopes.run(ctx, frame, executable, report)

    return self.unsupported(executable)

  def unsupported(self, executable: Executable) -> NoReturn:
    raise TypeError(
      f"Unsupported executable: {type(executable).__name__}"
    )