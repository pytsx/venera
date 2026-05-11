from html import escape

class Tag:
  def __init__(self, tag: str, *children: "Tag", **attrs):
    self.tag = tag
    self.children = children
    self.attrs = attrs

  def mount_attrs(self):
    if not self.attrs:
      return ""

    attrs = []
    for key, value in self.attrs.items():
      if key == "className":
        key = "class"
      else:
        key = key.replace("_", "-")

      attrs.append(f'{key}="{value}"')
    return " " + " ".join(attrs)

  def mount(self):
    children_html = "".join(
      child.mount() if hasattr(child, "mount") else escape(str(child))
      for child in self.children
    )
    return  f"""
      <{self.tag} {self.mount_attrs()}>
        {children_html}
      </{self.tag}>
    """
