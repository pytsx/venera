from dataclasses import dataclass, field


@dataclass(frozen=True)
class ThemeStyle:
  value: str = ""

  def extend(self, extra: str = "") -> str:
    return self.value + extra


@dataclass(frozen=True)
class HeadingTheme:
  h1: ThemeStyle = field(default_factory=ThemeStyle)
  h2: ThemeStyle = field(default_factory=ThemeStyle)
  h3: ThemeStyle = field(default_factory=ThemeStyle)
  h4: ThemeStyle = field(default_factory=ThemeStyle)
  h5: ThemeStyle = field(default_factory=ThemeStyle)


@dataclass(frozen=True)
class LayoutTheme:
  row: ThemeStyle = field(default_factory=ThemeStyle)
  grid: ThemeStyle = field(default_factory=ThemeStyle)


@dataclass(frozen=True)
class VariantTheme:
  default: ThemeStyle = field(default_factory=ThemeStyle)
  success: ThemeStyle = field(default_factory=ThemeStyle)
  error: ThemeStyle = field(default_factory=ThemeStyle)
  warning: ThemeStyle = field(default_factory=ThemeStyle)
  info: ThemeStyle = field(default_factory=ThemeStyle)


@dataclass(frozen=True)
class FieldTheme:
  container: ThemeStyle = field(default_factory=ThemeStyle)
  label: ThemeStyle = field(default_factory=ThemeStyle)
  value: ThemeStyle = field(default_factory=ThemeStyle)


@dataclass(frozen=True)
class DetailsTheme:
  container: ThemeStyle = field(default_factory=ThemeStyle)
  summary: ThemeStyle = field(default_factory=ThemeStyle)
  body: ThemeStyle = field(default_factory=ThemeStyle)

@dataclass(frozen=True)
class MetricTheme:
  container: ThemeStyle = field(default_factory=ThemeStyle)
  label: ThemeStyle = field(default_factory=ThemeStyle)
  value: ThemeStyle = field(default_factory=ThemeStyle)


@dataclass(frozen=True)
class ListTheme:
  container: ThemeStyle = field(default_factory=ThemeStyle)
  title: ThemeStyle = field(default_factory=ThemeStyle)
  item: ThemeStyle = field(default_factory=ThemeStyle)
  empty: ThemeStyle = field(default_factory=ThemeStyle)

@dataclass(frozen=True)
class Theme:
  name: str

  app: ThemeStyle = field(default_factory=ThemeStyle)

  heading: HeadingTheme = field(default_factory=HeadingTheme)
  layout: LayoutTheme = field(default_factory=LayoutTheme)

  card: VariantTheme = field(default_factory=VariantTheme)
  box: VariantTheme = field(default_factory=VariantTheme)
  section: VariantTheme = field(default_factory=VariantTheme)
  badge: VariantTheme = field(default_factory=VariantTheme)

  metric: MetricTheme = field(default_factory=MetricTheme)
  list: ListTheme = field(default_factory=ListTheme)

  _field: ThemeStyle = field(default_factory=ThemeStyle)
  details: DetailsTheme = field(default_factory=DetailsTheme)
  summary: ThemeStyle = field(default_factory=ThemeStyle)
  code: ThemeStyle = field(default_factory=ThemeStyle)