from typing import Optional
from datetime import datetime
from file_manager import FileManager

from utils import (
    singleton,
    eLogLevel,
    eFileType,
    eDirType,
    filename_from_enum,
    format_enum
)


def TRACE_LOG(level: Optional[eLogLevel], message: str):
    """Global function for logging."""
    Log().log(level, message)


@singleton
class Log:
    """
    Log class that handles logging messages to files based on severity.
    """

    def __init__(self):
        self._log_message: Optional[str] = None
        self.manager_instance = FileManager()
        self.manager_instance.set_working_path(eDirType.DIR_TYPE_LOG)
        self.min_level = eLogLevel.LOG_LEVEL_LOG

    def log(self, level: Optional[eLogLevel], message: str) -> None:
        """
        Logs a message with an optional log level.

        Args:
            level (Optional[eLogLevel]): Severity level.
            message (str): Message content.
        """
        if level is not None and not isinstance(level, eLogLevel):
            raise ValueError("Invalid log level")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if level is None:
            formatted = f"[{timestamp}] {message}"
        else:
            formatted = f"[{timestamp}] [{format_enum(level)}] -> {message}"

        file_type_map = {
            eLogLevel.LOG_LEVEL_LOG: eFileType.FILE_LOG,
            eLogLevel.LOG_LEVEL_WARNING: eFileType.FILE_LOG,
            eLogLevel.LOG_LEVEL_ERROR: eFileType.FILE_SYSERR,
        }

        file_type = file_type_map.get(level, eFileType.FILE_LOG)
        target_filename = filename_from_enum(file_type)

        if level is not None and level.value < self.min_level.value:
            return

        self.manager_instance.write_file(target_filename, formatted)

        if level is not None and file_type != eFileType.FILE_LOG:
            self.manager_instance.write_file(filename_from_enum(eFileType.FILE_LOG), formatted)

        print(formatted)
        self._log_message = formatted

    @property
    def last_message(self) -> Optional[str]:
        """Returns the last logged message."""
        return self._log_message


if __name__ == "__main__":
    """
    Debugging and manual testing block.
    """
    TRACE_LOG(eLogLevel.LOG_LEVEL_ERROR, "There was an issue.")
    TRACE_LOG(eLogLevel.LOG_LEVEL_LOG, "Log")
    TRACE_LOG(eLogLevel.LOG_LEVEL_WARNING, "Warning")
