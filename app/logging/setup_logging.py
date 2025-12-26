import logging
import re

from app.configs.configs import find_root
from app.configs.gitmastery_config import GITMASTERY_CONFIG_NAME


class GitMasteryFileHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        gitmastery_root = find_root(GITMASTERY_CONFIG_NAME)
        if gitmastery_root is None:
            return

        log_path = gitmastery_root[0] / ".gitmastery.log"
        handler = logging.FileHandler(log_path, mode="a")
        # TODO: This feels inefficient for logging but I can't think of a good
        # alternative
        handler.setFormatter(self.formatter)
        handler.emit(record)
        handler.close()

    def close(self) -> None:
        super().close()


class RemoveAnsiFilter(logging.Filter):
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")

    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = self.ansi_escape.sub("", record.msg)
        return True


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

    file_handler = GitMasteryFileHandler()
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RemoveAnsiFilter())
    root_logger.addHandler(file_handler)
