from typing import Optional, Tuple

from utils import (
    singleton,
    eLogLevel,
    eFileType,
    eDirType,
    filename_from_enum,
    format_enum
)

from datetime import datetime
from file_manager import FileManager

@singleton
class Log:
    """
    Log class implementation
    """
    def __init__(self):
        """
        Initializes the log class.

        Attributes:
            log_message (Optional[str]): Last log message.
            manager_instance (FileManager): File manager singleton.
            min_level (eLogLevel): Minimal log level for filtering.
        """

        self._log_message: Optional[str] = None
        self.manager_instance = FileManager()

        self.manager_instance.set_working_path(eDirType.DIR_TYPE_LOG)

        # min_level is supposed to change the minimal captured logs
        # if given log_level in arg passed in trace_log is higher than LOG_LEVEL_ERROR
        # it does not pass and is skipped.
        self.min_level = eLogLevel.LOG_LEVEL_LOG

    @property
    def TRACE_LOG(self) -> Optional[str]:
        """
        Returns logged message.

        :returns: Log message with log level.
        :rtype: Optional[str]
        """

        return self._log_message

    @TRACE_LOG.setter
    def TRACE_LOG(self, value: Tuple[Optional[eLogLevel], str]):
        """
        Sets log message with log level, writes the logs to target file based set log level.

        :param: value
        :type: Tuple[Optional[eLogLevel], str]
        """

        log_level, log_message = value

        if log_level is not None and not isinstance(log_level, eLogLevel):
            raise ValueError("Invalid log level")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if log_level is None:
            self._log_message = f"[{timestamp}] {log_message}"
            print(self._log_message)
            return

        formatted = f"[{timestamp}] [{format_enum(log_level)}] -> {log_message}"

        file_type_map = {
            eLogLevel.LOG_LEVEL_LOG: eFileType.FILE_LOG,
            eLogLevel.LOG_LEVEL_WARNING: eFileType.FILE_LOG,
            eLogLevel.LOG_LEVEL_ERROR: eFileType.FILE_SYSERR,
        }

        file_type = file_type_map.get(log_level, eFileType.FILE_LOG)
        target_filename = filename_from_enum(file_type)

        if log_level < self.min_level:
            return

        self.manager_instance.write_file(target_filename, formatted)

        if file_type != eFileType.FILE_LOG:
            self.manager_instance.write_file(filename_from_enum(eFileType.FILE_LOG), formatted)

        print(formatted)
        self._log_message = formatted


if __name__ == "__main__":
    """
    Debugging and manual testing block.
    """

    log_instance = Log()
    log_instance.TRACE_LOG = (eLogLevel.LOG_LEVEL_ERROR, "There was an issue.")
    log_instance.TRACE_LOG = (eLogLevel.LOG_LEVEL_LOG, "Log")
    log_instance.TRACE_LOG = (eLogLevel.LOG_LEVEL_WARNING, "Warning")
