from abc import ABC
from typing import Any, ClassVar, get_args, get_origin

from ..sdk import reference


class Executable[I, O](ABC):
  __input_type__: ClassVar[Any] = Any
  __output_type__: ClassVar[Any] = Any

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)

    for base in getattr(cls, "__orig_bases__", ()):
      origin = get_origin(base)
      args = get_args(base)

      if origin is None:
        continue

      if not isinstance(origin, type):
        continue

      if not issubclass(origin, Executable):
        continue

      if len(args) >= 2:
        cls.__input_type__ = args[0]
        cls.__output_type__ = args[1]

  def __init__(self, id: str | None = None):
    self.id = id or reference.getReference(type(self))