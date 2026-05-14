from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

T = TypeVar("T")


@dataclass(frozen=True)
class SourceKey(Generic[T]):
  name: str


class Source(Generic[T]):
  key: SourceKey[T]
  close_errors_are_fatal: bool = False

  def open(self, ctx) -> T:
    raise NotImplementedError

  def close(self, ctx, resource: T) -> None:
    pass


class SourceRegistry:
  def __init__(self):
    self._frames: list[dict[str, object]] = [{}]

  def push(self) -> None:
    self._frames.append({})

  def pop(self) -> dict[str, object]:
    if len(self._frames) == 1:
      raise RuntimeError("cannot pop root source frame")

    return self._frames.pop()

  def register(self, key: SourceKey[T], resource: T) -> None:
    current = self._frames[-1]

    if key.name in current:
      raise KeyError(f"source already registered in current scope: {key.name}")

    current[key.name] = resource

  def get(self, key: SourceKey[T]) -> T:
    for frame in reversed(self._frames):
      if key.name in frame:
        return cast(T, frame[key.name])

    raise KeyError(f"Source not found: {key.name}")

  def has(self, key: SourceKey[Any]) -> bool:
    return any(key.name in frame for frame in reversed(self._frames))

  def unregister(self, key: SourceKey[Any]) -> None:
    self._frames[-1].pop(key.name, None)