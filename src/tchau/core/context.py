from __future__ import annotations

from typing import Any, TypeVar

from ..sdk import logger

from .error import ErrorDecision
from .source import SourceKey, SourceRegistry

T = TypeVar("T")

class Context:
  def __init__(self, log: logger.Logger):
    self.log: logger.Logger = log
    self.data: dict[str, Any] = {}

    self.read_keys: set[str] = set()
    self.written_keys: set[str] = set()

    self.sources = SourceRegistry()

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

  def source(self, key: SourceKey[T]) -> T:
    return self.sources.get(key)

  def has_source(self, key: SourceKey[Any]) -> bool:
    return self.sources.has(key)

  def register_source(self, key: SourceKey[T], resource: T) -> None:
    self.sources.register(key, resource)

  def push_source_scope(self) -> None:
    self.sources.push()

  def pop_source_scope(self) -> dict[str, object]:
    return self.sources.pop()

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
  
  def source(self, key: SourceKey[T]) -> T:
    return self._ctx.source(key)

  def has_source(self, key: SourceKey[Any]) -> bool:
    return self._ctx.has_source(key)