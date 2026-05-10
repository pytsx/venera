from pathlib import Path 
from typing import Any
import polars as pl 
from typing import Callable

from pipefy.sdk import logger

from error import ErrorDecision

df_readers: dict[str, Callable[[Path], pl.DataFrame]] = {
  ".xlsx": pl.read_excel,
  ".xls": pl.read_excel,
  ".csv": pl.read_csv,
  ".parquet": pl.read_parquet,
}

class Context:
  def __init__(self, log: logger.Logger):
    self.log: logger.Logger = log
    self.data: dict[str, Any] = {}

    self.read_keys: set[str] = set()
    self.written_keys: set[str] = set()

  def begin_tracking(self) -> None:
    self.read_keys = set()
    self.written_keys = set()

  def get(self, key: str) -> Any:
    self.read_keys.add(key)

    if key not in self.data:
      raise KeyError(f"Context key not found: {key}")

    return self.data[key]

  def set(self, key: str, value: Any) -> None:
    self.written_keys.add(key)
    self.data[key] = value

  def has(self, key: str) -> bool:
    return key in self.data

class ErrorContext:
  def __init__(self, ctx: Context, exc: Exception):
    self.error = exc 
    self._ctx = ctx

  def get(self, key: str):
    return self._ctx.get(key)

  def set(self, key: str, value):
    return self._ctx.set(key, value)

  def has(self, key: str):
    return self._ctx.has(key)

  def abort(self, reason: str | None = None):
    return ErrorDecision("abort", reason or str(self.error))

  def retry(self, max_retries: int = 1, reason: str | None = None):
    return ErrorDecision("retry", reason or str(self.error), max_retries)

  def continue_(self, reason: str | None = None):
    return ErrorDecision("continue", reason or str(self.error))

  def skip(self, reason: str | None = None):
    return ErrorDecision("skip", reason or str(self.error))
  
  def is_(self, error_type: type[Exception]) -> bool:
    return isinstance(self.error, error_type)