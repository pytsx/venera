from abc import ABC, abstractmethod
from ..sdk import reference

class Executable(ABC):
  def __init__(self, id: str | None = None):
    self.id = id or reference.getReference(type(self))