from pipefy.middleware import middleware

class MiddlewareEngine:
  def __init__(self, *mw: middleware.Middleware):
    self.middlewares = mw
    self.listeners: dict[str, list[middleware.Middleware]] = self._index_middlewares(self.middlewares)

  def _index_middlewares(self, middlewares: tuple[middleware.Middleware, ...]):
    listeners = {}

    for mw in middlewares:
      for event in mw.events:
        listeners.setdefault(event, []).append(mw)

    return listeners

  def emit(self, hook: middleware.MiddlewareEvent, *args) -> None:
    for mw in self._listeners(hook):
      getattr(mw, hook)(*args)

  def every(self, hook: middleware.MiddlewareEvent, *args) -> bool:
    for mw in self._listeners(hook):
      result = getattr(mw, hook)(*args)

      if result is False:
        return False

    return True

  def emit_transform(self, hook: middleware.MiddlewareEvent, value):
    result = value

    for mw in self._listeners(hook):
      result = getattr(mw, hook)(result)

      if result is None:
        raise TypeError(f"{mw.__class__.__name__}.{hook} must return a value")

    return result

  def _listeners(self, hook: middleware.MiddlewareEvent):
    return self.listeners.get(hook, ())