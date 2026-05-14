from __future__ import annotations

from typing import Any, TypeVar, Generic

from ..sdk import logger
from dataclasses import dataclass

from .error import ErrorDecision
from .source import SourceKey, SourceRegistry

T = TypeVar("T")

@dataclass(frozen=True)
class CtxKey(Generic[T]):
  name: str

class Context:
  def __init__(self, log: logger.Logger):
    self.log: logger.Logger = log
    self.data: dict[str, Any] = {}

    self.read_keys: set[str] = set()
    self.written_keys: set[str] = set()

    self.sources = SourceRegistry()

  def _key_name(self, key: str | CtxKey[Any]) -> str:
    if isinstance(key, CtxKey):
      return key.name

    return key

  def begin_tracking(self) -> None:
    self.read_keys = set()
    self.written_keys = set()

  @overload
  def get(self, key: CtxKey[T]) -> T:
    ...

  @overload
  def get(self, key: str) -> Any:
    ...

  def get(self, key: str | CtxKey[T]) -> Any:
    name = self._key_name(key)
    self.read_keys.add(name)

    if name not in self.data:
      raise KeyError(f"Context key not found: {name}")

    return self.data[name]

  def set(self, key: str | CtxKey[T], value: T) -> None:
    name = self._key_name(key)
    self.written_keys.add(name)
    self.data[name] = value

  def has(self, key: str | CtxKey[Any]) -> bool:
    return self._key_name(key) in self.data

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

  def get(self, key: str | CtxKey[T]) -> T:
    return self._ctx.get(key)

  def set(self, key: str | CtxKey[T], value: T) -> None:
    self._ctx.set(key, value)

  def has(self, key: str | CtxKey[Any]) -> bool:
    return self._ctx.has(key)

  def abort(self, reason: str | None = None):
    return ErrorDecision("abort", reason or str(self.error))

  def retry(self, max_retries: int = 1, reason: str | None = None):
    return ErrorDecision("retry", reason or str(self.error), max_retries)

  def recover(self, reason: str | None = None):
    return ErrorDecision("recover", reason or str(self.error))

  def is_(self, error_type: type[Exception]) -> bool:
    return isinstance(self.error, error_type)

  def source(self, key: SourceKey[T]) -> T:
    return self._ctx.source(key)

  def has_source(self, key: SourceKey[Any]) -> bool:
    return self._ctx.has_source(key)