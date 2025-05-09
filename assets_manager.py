from utils import (
    singleton,
    working_directories,
    require_conditions,
    DEBUG_MODE,
    eLogLevel
)

from typing import Optional, Any
from log import TRACE_LOG
import os

class AssetsManager:
    def __init__(self):
        self._path: Optional[str] = ""
        self._file: Optional[str] = None

    @property
    def path(self) -> Optional[str]:
        if DEBUG_MODE:
            TRACE_LOG(eLogLevel.LOG_LEVEL_LOG, f"AssetsManager.path -> {self._path}")
        return self._path

    @path.setter
    def path(self, path: Optional[str]):
        if DEBUG_MODE:
            TRACE_LOG(eLogLevel.LOG_LEVEL_LOG, f"AssetsManager.path -> setting self._path to: {path}")
            self._path = path

    @require_conditions
    def load_file(self, asset: Optional[Any]) -> bool:
        file = os.path.join(self._path, asset)
