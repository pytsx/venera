from dataclasses import dataclass, field, asdict

from ..sdk.html.ui import UI, HTMLPage
from ..sdk.html.themes.default import default_theme

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
    html_tag = to_html(self, HTMLPage())
    return html_tag.mount()
  




def to_html(res: PipelineReport, page: HTMLPage):
  ui = UI(page, default_theme)

  return ui.app(
    ui.heading("Pipeline Report", level=1),
    _summary_to_html(res, ui),
    *[_pipeline_node_to_html(node, ui) for node in res.nodes],
  )


def _summary_to_html(res: PipelineReport, ui: UI):
  return ui.card(
    ui.row(
      ui.field("Status geral", ""),
      ui.badge(_status_text(res.success), variant=_status_variant(res.success)),
    ),
    ui.grid(
      ui.metric("Nodes", res.nodes_total),
      ui.metric("Sucesso", res.nodes_success),
      ui.metric("Falha", res.nodes_failed),
      ui.metric("Duração", _format_ms(res.duration_ms)),
      min_width=140,
    ),
    ui.row(
      ui.field("Início", res.started_at),
      ui.field("Fim", res.ended_at),
    ),
  )


def _pipeline_node_to_html(node: PipelineNodeReport, ui: UI):
  return ui.card(
    ui.row(
      ui.heading(f"Node: {node.node_id}", level=2),
      ui.badge(_status_text(node.success), variant=_status_variant(node.success)),
      justify="between",
    ),
    ui.row(
      ui.field("Início", node.started_at),
      ui.field("Fim", node.ended_at),
      ui.field("Duração", _format_ms(node.duration_ms)),
    ),
    ui.grid(
      ui.list("Inputs declarados", node.inputs_declared),
      ui.list("Outputs declarados", node.outputs_declared),
      ui.list("Context antes", node.context_keys_before),
      ui.list("Context depois", node.context_keys_after),
      min_width=220,
    ),
    ui.grid(
      ui.list("Missing inputs", node.missing_inputs),
      ui.list("Missing outputs", node.missing_outputs),
      ui.list("Undeclared outputs", node.undeclared_outputs),
      min_width=220,
    ),
    ui.details(
      "Steps",
      *[_pipeline_step_to_html(step, ui) for step in node.steps],
    ),
    variant=_card_variant(node.success),
  )


def _pipeline_step_to_html(step: PipelineStepReport, ui: UI):
  children = [
    ui.row(
      ui.heading(step.name, level=4),
      ui.badge(_status_text(step.success), variant=_status_variant(step.success)),
      justify="between",
    ),
    ui.field("Reference", step.reference),
    ui.row(
      ui.field("Início", step.started_at),
      ui.field("Fim", step.ended_at),
      ui.field("Duração", _format_ms(step.duration_ms)),
    ),
  ]

  if step.handler_reference:
    children.append(ui.field("Handler", step.handler_reference))

  if step.decision:
    children.append(
      ui.row(
        ui.field("Decisão", step.decision),
        ui.field("Motivo", step.decision_reason),
        ui.field("Corrigido", _bool_text(step.fixed)),
      )
    )

  if step.error:
    children.append(_error_to_html(step.error, ui))

  if step.retries:
    children.append(
      ui.details(
        "Retries",
        *[_retry_to_html(retry, ui) for retry in step.retries],
      )
    )

  return ui.card(*children, variant=_card_variant(step.success))


def _error_to_html(err: PipelineErrorReport, ui: UI):
  children = [
    ui.heading("Erro", level=5),
    ui.field("Tipo", err.type),
    ui.field("Mensagem", err.message),
  ]

  if err.cause_type or err.cause_message:
    children.append(
      ui.field("Causa", f"{err.cause_type or ''}: {err.cause_message or ''}")
    )

  if err.traceback:
    children.append(ui.details("Traceback", ui.code(err.traceback)))

  return ui.box(*children, variant="error")


def _retry_to_html(retry: PipelineRetryReport, ui: UI):
  children = [
    ui.row(
      ui.field("Tentativa", retry.attempt),
      ui.badge(_status_text(retry.success), variant=_status_variant(retry.success)),
      justify="between",
    ),
    ui.field("Duração", _format_ms(retry.duration_ms)),
  ]

  if retry.error:
    children.append(_error_to_html(retry.error, ui))

  return ui.card(*children, variant=_card_variant(retry.success))


def _status_text(success: bool):
  return "Sucesso" if success else "Falhou"


def _status_variant(success: bool):
  return "success" if success else "error"


def _card_variant(success: bool):
  return "success" if success else "error"


def _format_ms(value: float | None):
  if value is None:
    return ""

  if value < 1000:
    return f"{value:.2f} ms"

  return f"{value / 1000:.2f} s"


def _bool_text(value: bool | None):
  if value is None:
    return ""

  return "Sim" if value else "Não"