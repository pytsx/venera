import logging
from pathlib import Path
from typing import Callable, Any

class Logger:
  def __init__(self, pkg: str, level: int = logging.INFO):
    parts = pkg.split(".")

    file_name = parts[-1]
    folders = parts[:-1]

    log_dir = Path.cwd() / ".logs"

    for folder in folders:
      log_dir = log_dir / folder

    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{file_name}.log"

    self.logger = logging.getLogger(pkg)
    self.logger.setLevel(level)
    self.logger.propagate = False

    if self.logger.handlers:
      return

    formatter = logging.Formatter(
      "[%(name)s:%(levelname)s] %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    self.logger.addHandler(file_handler)
    self.logger.addHandler(stream_handler)

  def log(
    self,
    func: Callable[[str], None],
    ref: str,
    *args: Any,
  ) -> None:
    message = " ".join(str(arg) for arg in args)
    func(f"[{ref}] {message}")

  def info(self, ref: str, *msg: Any) -> None:
    self.log(self.logger.info, ref, *msg)

  def error(self, ref: str, *msg: Any) -> None:
    self.log(self.logger.error, ref, *msg)

  def warn(self, ref: str, *msg: Any) -> None:
    self.log(self.logger.warning, ref, *msg)

  def warning(self, ref: str, *msg: Any) -> None:
    self.warn(ref, *msg)

  def critical(self, ref: str, *msg: Any) -> None:
    self.log(self.logger.critical, ref, *msg)

  def debug(self, ref: str, *msg: Any) -> None:
    self.log(self.logger.debug, ref, *msg)