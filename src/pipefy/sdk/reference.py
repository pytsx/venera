from typing import Any 
from types import ModuleType
import sys 

def getReference(obj: Any) -> str:
    module_name = obj.__module__

    module: ModuleType | None = sys.modules.get(module_name)

    if module_name == "__main__" and module is not None and module.__spec__ is not None:
        module_name = module.__spec__.name

    return f"{module_name}:{obj.__qualname__}"