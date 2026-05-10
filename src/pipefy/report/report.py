from dataclasses import dataclass, field, asdict
from src.pipefy.report import report

@dataclass
class PipelineErrorReport:
  type: str
  message: str
  traceback: str | None = None
  cause_type: str | None = None
  cause_message: str | None = None


@dataclass
class PipelineRetryReport:
  attempt: int
  success: bool
  error: PipelineErrorReport | None = None
  duration_ms: float | None = None

@dataclass
class PipelineStepReport:
  name: str
  reference: str
  success: bool

  started_at: str | None = None
  ended_at: str | None = None
  duration_ms: float | None = None

  error: PipelineErrorReport | None = None

  handler_reference: str | None = None
  decision: str | None = None
  decision_reason: str | None = None
  fixed: bool | None = None

  retries: list[PipelineRetryReport] = field(default_factory=list)

  def to_dict(self) -> dict:
    return asdict(self)


@dataclass
class PipelineNodeReport:
  node_id: str
  success: bool = True

  started_at: str | None = None
  ended_at: str | None = None
  duration_ms: float | None = None

  inputs_declared: list[str] = field(default_factory=list)
  outputs_declared: list[str] = field(default_factory=list)

  context_keys_before: list[str] = field(default_factory=list)
  context_keys_after: list[str] = field(default_factory=list)

  missing_inputs: list[str] = field(default_factory=list)
  missing_outputs: list[str] = field(default_factory=list)
  undeclared_outputs: list[str] = field(default_factory=list)

  steps: list[PipelineStepReport] = field(default_factory=list)

  undeclared_inputs: list[str] = field(default_factory=list)

  def to_dict(self) -> dict:
    return asdict(self)


@dataclass
class PipelineReport:
  success: bool = True

  started_at: str | None = None
  ended_at: str | None = None
  duration_ms: float | None = None

  nodes_total: int = 0
  nodes_success: int = 0
  nodes_failed: int = 0

  nodes: list[PipelineNodeReport] = field(default_factory=list)

  @property
  def failed_node(self) -> PipelineNodeReport | None:
    for node in self.nodes:
      if not node.success:
        return node
    return None

  def to_dict(self) -> dict:
    return asdict(self)

  def to_html(self) -> str:
    html_tag = report.html.to_html(self, report.html.HTMLPage())
    return html_tag.mount()