from ..core.middleware import Middleware, MiddlewareEvent

class MiddlewareEngine:
  def __init__(self, *mw: Middleware):
    self.middlewares = mw
    self.listeners: dict[str, list[Middleware]] = self._index_middlewares(self.middlewares)

  def _index_middlewares(self, middlewares: tuple[Middleware, ...]):
    listeners = {}

    for mw in middlewares:
      for event in mw.events():
        listeners.setdefault(event, []).append(mw)

    return listeners

  def emit(self, hook: MiddlewareEvent, *args) -> None:
    for mw in self._listeners(hook):
      getattr(mw, hook)(*args)

  def every(self, hook: MiddlewareEvent, *args) -> bool:
    for mw in self._listeners(hook):
      result = getattr(mw, hook)(*args)

      if result is False:
        return False

    return True

  def emit_transform(self, hook: MiddlewareEvent, value):
    result = value

    for mw in self._listeners(hook):
      result = getattr(mw, hook)(result)

      if result is None:
        raise TypeError(f"{mw.__class__.__name__}.{hook} must return a value")

    return result

  def _listeners(self, hook: MiddlewareEvent):
    return self.listeners.get(hook, ())