from pipefy.sdk import reference
from pipefy.middleware import middleware

class LoggerMiddleware(middleware.Middleware):
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
    ctx.log.info(reference.getReference(action), "started")

  def afterRunStep(self, ctx, r, name, action):
    ctx.log.info(reference.getReference(action), "success" if r.success else "failed")

  def onStepError(self, ctx, r, err, error_handler):
    ctx.log.error(r.reference, type(err).__name__, str(err))

  def beforeRetry(self, ctx, r, attempt, max_retries, action):
    ctx.log.info(reference.getReference(action), f"retry {attempt}/{max_retries}")

  def afterRetry(self, ctx, r, attempt, max_retries, action):
    ctx.log.info(reference.getReference(action), f"retry {attempt}/{max_retries} success")

  def onRetryError(self, ctx, r, err, attempt, max_retries, action):
    ctx.log.error(reference.getReference(action), f"retry {attempt}/{max_retries} failed:", err)

