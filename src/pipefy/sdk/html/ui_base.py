from src.pipefy.sdk.html.page import HTMLPage

class UIBase:
  def __init__(self, page: HTMLPage):
    self.page = page

  def badge(self, text: str, **attrs):
    return self.page.span(text, **attrs)

  def card(self, *children, **attrs):
    return self.page.div(*children, **attrs)

  def section(self, title: str, *children, **attrs):
    return self.page.section(
      self.page.h2(title),
      *children,
      **attrs,
    )

  def row(self, *children, **attrs):
    return self.page.div(*children, **attrs)

  def grid(self, *children, **attrs):
    return self.page.div(*children, **attrs)

  def metric(
    self,
    label: str,
    value: object,
    *,
    container_style: str = "",
    label_style: str = "",
    value_style: str = "",
  ):
    return self.page.div(
      self.page.div(
        label,
        style=label_style,
      ),
      self.page.div(
        "" if value is None else str(value),
        style=value_style,
      ),
      style=container_style,
    )

  def field(self, label: str, value: object, **attrs):
    return self.page.span(
      self.page.strong(f"{label}: "),
      "" if value is None else str(value),
      **attrs,
    )

  def list(self, title: str, items: list[str], **attrs):
    if not items:
      return self.page.div(
        self.page.strong(f"{title}: "),
        self.page.span("Nenhum"),
        **attrs,
      )

    return self.page.div(
      self.page.strong(f"{title}:"),
      self.page.ul(
        *[self.page.li(item) for item in items],
      ),
      **attrs,
    )

  def details(
    self,
    title: str,
    *children,
    container_style: str = "",
    summary_style: str = "",
    body_style: str = "",
  ):
    return self.page.details(
      self.page.summary(
        title,
        style=summary_style,
      ),
      self.page.div(
        *children,
        style=body_style,
      ),
      style=container_style,
    )

  def code(self, value: str, **attrs):
    return self.page.pre(value, **attrs)

  def heading(self, text: str, level: int = 1, **attrs):
    tag = getattr(self.page, f"h{level}")
    return tag(text, **attrs)