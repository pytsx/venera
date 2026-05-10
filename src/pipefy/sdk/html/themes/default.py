from pipefy.sdk.html.theme import (
  Theme,
  ThemeStyle,
  HeadingTheme,
  LayoutTheme,
  VariantTheme,
  MetricTheme,
  ListTheme,
  DetailsTheme
)


default_theme = Theme(
  name="default",

  app=ThemeStyle(
    "font-family:Arial,Helvetica,sans-serif;"
    "background:#f9fafb;"
    "color:#111827;"
    "padding:28px;"
    "border-radius:12px;"
    "max-width:1100px;"
    "margin:0 auto;"
    "display:flex;"
    "flex-direction:column;"
    "gap:20px;"
  ),

  heading=HeadingTheme(
    h1=ThemeStyle(
      "margin:0 0 20px 0;"
      "font-size:28px;"
      "color:#111827;"
    ),
    h2=ThemeStyle(
      "margin:0;"
      "font-size:22px;"
      "color:#111827;"
    ),
    h3=ThemeStyle(
      "margin:18px 0 12px 0;"
      "font-size:18px;"
      "color:#111827;"
    ),
    h4=ThemeStyle(
      "margin:0;"
      "font-size:16px;"
      "color:#111827;"
    ),
    h5=ThemeStyle(
      "margin:0 0 8px 0;"
      "font-size:15px;"
      "color:#991b1b;"
    ),
  ),

  layout=LayoutTheme(
    row=ThemeStyle(
      "display:flex;"
      "flex-wrap:wrap;"
      "gap:16px;"
      "align-items:center;"
    ),
    grid=ThemeStyle(
      "display:grid;"
      "gap:12px;"
    ),
  ),

  card=VariantTheme(
    default=ThemeStyle(
      "background:#ffffff;"
      "border:1px solid #e5e7eb;"
      "border-radius:12px;"
      "padding:18px;"
      "box-shadow:0 1px 3px rgba(0,0,0,0.06);"
      "display:flex;"
      "flex-direction:column;"
      "gap:14px;"
    ),
    success=ThemeStyle(
      "background:#f0fdf4;"
      "border:1px solid #22c55e;"
      "border-left:6px solid #22c55e;"
      "border-radius:10px;"
      "padding:18px;"
      "box-shadow:0 1px 3px rgba(0,0,0,0.08);"
      "display:flex;"
      "flex-direction:column;"
      "gap:14px;"
    ),
    error=ThemeStyle(
      "background:#fef2f2;"
      "border:1px solid #ef4444;"
      "border-left:6px solid #ef4444;"
      "border-radius:10px;"
      "padding:18px;"
      "box-shadow:0 1px 3px rgba(0,0,0,0.08);"
      "display:flex;"
      "flex-direction:column;"
      "gap:14px;"
    ),
  ),

  box=VariantTheme(
    default=ThemeStyle(
      "background:#ffffff;"
      "border:1px solid #e5e7eb;"
      "border-radius:8px;"
      "padding:14px;"
      "display:flex;"
      "flex-direction:column;"
      "gap:8px;"
    ),
    error=ThemeStyle(
      "margin-top:12px;"
      "background:#fee2e2;"
      "border:1px solid #fecaca;"
      "border-radius:8px;"
      "padding:14px;"
      "display:flex;"
      "flex-direction:column;"
      "gap:8px;"
    ),
  ),

  section=VariantTheme(
    default=ThemeStyle(
      "background:#ffffff;"
      "border:1px solid #e5e7eb;"
      "border-radius:12px;"
      "padding:18px;"
      "margin-bottom:20px;"
      "box-shadow:0 1px 3px rgba(0,0,0,0.06);"
    ),
    success=ThemeStyle(
      "background:#f0fdf4;"
      "border:1px solid #22c55e;"
      "border-left:6px solid #22c55e;"
      "border-radius:10px;"
      "padding:18px;"
      "box-shadow:0 1px 3px rgba(0,0,0,0.08);"
    ),
    error=ThemeStyle(
      "background:#fef2f2;"
      "border:1px solid #ef4444;"
      "border-left:6px solid #ef4444;"
      "border-radius:10px;"
      "padding:18px;"
      "box-shadow:0 1px 3px rgba(0,0,0,0.08);"
    ),
  ),

  badge=VariantTheme(
    default=ThemeStyle(
      "display:inline-block;"
      "background:#e5e7eb;"
      "color:#374151;"
      "font-weight:bold;"
      "padding:4px 10px;"
      "border-radius:999px;"
      "font-size:13px;"
    ),
    success=ThemeStyle(
      "display:inline-block;"
      "background:#dcfce7;"
      "color:#166534;"
      "font-weight:bold;"
      "padding:4px 10px;"
      "border-radius:999px;"
      "font-size:13px;"
    ),
    error=ThemeStyle(
      "display:inline-block;"
      "background:#fee2e2;"
      "color:#991b1b;"
      "font-weight:bold;"
      "padding:4px 10px;"
      "border-radius:999px;"
      "font-size:13px;"
    ),
  ),

  metric=MetricTheme(
    container=ThemeStyle(
      "background:#f9fafb;"
      "border:1px solid #e5e7eb;"
      "border-radius:10px;"
      "padding:12px;"
    ),
    label=ThemeStyle(
      "font-size:13px;"
      "color:#6b7280;"
      "margin-bottom:4px;"
    ),
    value=ThemeStyle(
      "font-size:20px;"
      "font-weight:bold;"
      "color:#111827;"
    ),
  ),

  _field=ThemeStyle(
    "font-size:14px;"
    "color:#374151;"
  ),

  list=ListTheme(
    container=ThemeStyle(
      "font-size:14px;"
      "background:#ffffff;"
      "padding:10px;"
      "border-radius:8px;"
      "border:1px solid #e5e7eb;"
      "max-height:180px;"
      "overflow:auto;"
    ),
    title=ThemeStyle(
      "display:block;"
      "margin-bottom:6px;"
      "color:#374151;"
    ),
    item=ThemeStyle(
      "margin:4px 0;"
      "color:#374151;"
    ),
    empty=ThemeStyle(
      "color:#6b7280;"
    ),
  ),

  details=DetailsTheme(
    container=ThemeStyle(
      "margin-top:8px;"
    ),
    summary=ThemeStyle(
      "cursor:pointer;"
      "font-weight:bold;"
      "color:#111827;"
      "margin-bottom:10px;"
    ),
    body=ThemeStyle(
      "display:flex;"
      "flex-direction:column;"
      "gap:12px;"
      "margin-top:10px;"
    ),
  ),

  summary=ThemeStyle(
    "cursor:pointer;"
    "font-weight:bold;"
    "color:#111827;"
    "margin-bottom:10px;"
  ),

  code=ThemeStyle(
    "white-space:pre-wrap;"
    "overflow:auto;"
    "max-height:360px;"
    "background:#450a0a;"
    "color:#fee2e2;"
    "padding:12px;"
    "border-radius:8px;"
    "font-size:12px;"
    "line-height:1.45;"
  ),
)