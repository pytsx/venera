from ..sdk import getReference
from ..core.middleware import Middleware

class LoggerMiddleware(Middleware):
  events = (
    "beforeRunPipeline",
    "afterRunPipeline",
    "beforeRunNode",
    "afterRunNode",
    "beforeRunStep",
    "afterRunStep",
    "onStepError",
    "beforeRetry",
    "afterRetry",
    "onRetryError",
  )
    
  def beforeRunPipeline(self, ctx, r):
    ctx.log.info("pipeline", "started")

  def afterRunPipeline(self, ctx, r):
    ctx.log.info("pipeline", "success" if r.success else "failed")

  def beforeRunNode(self, ctx, r, n):
    ctx.log.info(n.id, "started")

  def afterRunNode(self, ctx, r, n):
    ctx.log.info(n.id, "success" if r.success else "failed")

  def beforeRunStep(self, ctx, r, name, action):
    ctx.log.info(getReference(action), "started")

  def afterRunStep(self, ctx, r, name, action):
    ctx.log.info(getReference(action), "success" if r.success else "failed")

  def onStepError(self, ctx, r, err, error_handler):
    ctx.log.error(r.reference, type(err).__name__, str(err))

  def beforeRetry(self, ctx, r, attempt, max_retries, action):
    ctx.log.info(getReference(action), f"retry {attempt}/{max_retries}")

  def afterRetry(self, ctx, r, attempt, max_retries, action):
    ctx.log.info(getReference(action), f"retry {attempt}/{max_retries} success")

  def onRetryError(self, ctx, r, err, attempt, max_retries, action):
    ctx.log.error(getReference(action), f"retry {attempt}/{max_retries} failed:", err)

