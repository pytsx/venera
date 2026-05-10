from datetime import datetime
from time import perf_counter

from .middleware import Middleware
from ..sdk import getReference

class ReportTraceMiddleware(Middleware):
  events = (
    "beforeRunPipeline",
    "afterRunPipeline",
    "beforeRunNode",
    "afterRunNode",
    "beforeRunStep",
    "afterRunStep",
    "beforeRetry",
    "afterRetry",
    "onRetryError",
  )

  def __init__(self):
    self.pipeline_start: float | None = None
    self.node_start: dict[int, float] = {}
    self.step_start: dict[int, float] = {}
    self.retry_start: dict[int, float] = {}

  def now_iso(self) -> str:
    return datetime.now().isoformat(timespec="seconds")

  def beforeRunPipeline(self, ctx, r):
    self.pipeline_start = perf_counter()
    r.started_at = self.now_iso()

  def afterRunPipeline(self, ctx, r):
    r.ended_at = self.now_iso()

    if self.pipeline_start is not None:
      r.duration_ms = round((perf_counter() - self.pipeline_start) * 1000, 2)

    r.nodes_success = sum(1 for n in r.nodes if n.success)
    r.nodes_failed = sum(1 for n in r.nodes if not n.success)

  def beforeRunNode(self, ctx, r, n):
    self.node_start[id(r)] = perf_counter()
    r.started_at = self.now_iso()
    r.inputs_declared = list(n.inputs)
    r.outputs_declared = list(n.outputs)
    r.context_keys_before = sorted(ctx.data.keys())

  def afterRunNode(self, ctx, r, n):
    r.ended_at = self.now_iso()
    r.context_keys_after = sorted(ctx.data.keys())

    start = self.node_start.pop(id(r), None)
    if start is not None:
      r.duration_ms = round((perf_counter() - start) * 1000, 2)

  def beforeRunStep(self, ctx, r, name, action):
    self.step_start[id(r)] = perf_counter()
    r.started_at = self.now_iso()
    r.reference = getReference(action)

  def afterRunStep(self, ctx, r, name, action):
    r.ended_at = self.now_iso()

    start = self.step_start.pop(id(r), None)
    if start is not None:
      r.duration_ms = round((perf_counter() - start) * 1000, 2)

  def beforeRetry(self, ctx, r, attempt, max_retries, action):
    self.retry_start[id(r)] = perf_counter()

  def afterRetry(self, ctx, r, attempt, max_retries, action):
    start = self.retry_start.pop(id(r), None)
    if start is not None:
      r.duration_ms = round((perf_counter() - start) * 1000, 2)

  def onRetryError(self, ctx, r, err, attempt, max_retries, action):
    start = self.retry_start.pop(id(r), None)
    if start is not None:
      r.duration_ms = round((perf_counter() - start) * 1000, 2)

