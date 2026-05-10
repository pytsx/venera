from typing import Literal

from src.pipefy.sdk.html.page import HTMLPage
from src.pipefy.sdk.html.theme import Theme, ThemeStyle, VariantTheme
from src.pipefy.sdk.html.ui_base import UIBase

Variant = Literal["default", "success", "error", "warning", "info"]

class UI:
  def __init__(self, page: HTMLPage, theme: Theme):
    self.page = page
    self.theme = theme
    self.base = UIBase(page)

  def _style(self, style: ThemeStyle, extra: str = "") -> str:
    return style.extend(extra)

  def _variant_style(
    self,
    styles: VariantTheme,
    variant: Variant = "default",
  ) -> ThemeStyle:
    return getattr(styles, variant)

  def app(self, *children):
    return self.base.card(
      *children,
      style=self._style(self.theme.app),
    )

  def badge(self, text: str, variant: Variant = "default"):
    return self.base.badge(
      text,
      style=self._style(
        self._variant_style(self.theme.badge, variant),
      ),
    )

  def card(self, *children, variant: Variant = "default"):
    return self.base.card(
      *children,
      style=self._style(
        self._variant_style(self.theme.card, variant),
      ),
    )

  def box(self, *children, variant: Variant = "default"):
    return self.base.card(
      *children,
      style=self._style(
        self._variant_style(self.theme.box, variant),
      ),
    )

  def section(self, title: str, *children, variant: Variant = "default"):
    return self.base.section(
      title,
      *children,
      style=self._style(
        self._variant_style(self.theme.section, variant),
      ),
    )

  def row(self, *children, justify: str | None = None):
    extra = ""

    if justify == "between":
      extra = "justify-content:space-between;"

    return self.base.row(
      *children,
      style=self._style(self.theme.layout.row, extra),
    )

  def grid(self, *children, min_width: int = 180):
    return self.base.grid(
      *children,
      style=self._style(
        self.theme.layout.grid,
        f"grid-template-columns:repeat(auto-fit,minmax({min_width}px,1fr));",
      ),
    )

  def metric(self, label: str, value: object):
    return self.base.metric(
      label,
      value,
      container_style=self._style(self.theme.metric.container),
      label_style=self._style(self.theme.metric.label),
      value_style=self._style(self.theme.metric.value),
    )

  def field(self, label: str, value: object):
    return self.base.field(
      label,
      value,
      style=self._style(self.theme._field),
    )

  def list(self, title: str, items: list[str]):
    return self.base.list(
      title,
      items,
      style=self._style(self.theme.list.container),
    )

  def details(self, title: str, *children):
    return self.base.details(
      title,
      *children,
      container_style=self._style(self.theme.details.container),
      summary_style=self._style(self.theme.details.summary),
      body_style=self._style(self.theme.details.body),
    )

  def code(self, value: str):
    return self.base.code(
      value,
      style=self._style(self.theme.code),
    )

  def heading(self, text: str, level: int = 1):
    style_by_level = {
      1: self.theme.heading.h1,
      2: self.theme.heading.h2,
      3: self.theme.heading.h3,
      4: self.theme.heading.h4,
      5: self.theme.heading.h5,
    }

    return self.base.heading(
      text,
      level=level,
      style=self._style(style_by_level.get(level, self.theme.heading.h1)),
    )