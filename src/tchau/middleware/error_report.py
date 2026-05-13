from ..report.model import PipelineErrorReport
from ..sdk import getReference
from ..core.middleware import Middleware
import traceback 

class ErrorReportMiddleware(Middleware):

  def build_error_report(self, err: Exception) -> PipelineErrorReport:
    cause = err.__cause__ or err.__context__

    return PipelineErrorReport(
      type=type(err).__name__,
      message=str(err),
      traceback="".join(
        traceback.format_exception(type(err), err, err.__traceback__)
      ),
      cause_type=type(cause).__name__ if cause else None,
      cause_message=str(cause) if cause else None,
    )

  def onStepError(self, ctx, r, err, error_handler):
    r.success = False
    r.error = self.build_error_report(err)
    r.handler_reference = getReference(error_handler)

  def onRetryError(self, ctx, r, err, attempt, max_retries, action):
    r.success = False
    r.error = self.build_error_report(err)
