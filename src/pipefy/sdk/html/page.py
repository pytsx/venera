from .tag import Tag

class HTMLPage:
  def tag(self, name: str, *children, **attrs):
    return Tag(name, *children, **attrs)

  def __getattr__(self, name: str):
    if name.startswith("_"):
      return 

    def create_tag(*children, **attrs):
      return self.tag(name, *children, **attrs)

    return create_tag