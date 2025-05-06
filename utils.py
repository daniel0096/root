from typing import TypeVar, Callable, Dict, Any, Optional
from functools import wraps
from enum import Enum

DEBUG_MODE = 1

class eMenuState(Enum):
    """
    Enumeration for different menu states in the application.
    """
    MENU_STATE_NONE = 0
    MENU_STATE_MAIN = 1
    MENU_STATE_PLAY = 2
    MENU_STATE_OPTIONS = 3
    MENU_STATE_LEADER_BOARD = 4
    MENU_STATE_EXIT = 5


class eLogLevel(Enum):
    """
    Enumeration for log severity levels.
    """
    LOG_LEVEL_NONE = 0
    LOG_LEVEL_LOG = 1
    LOG_LEVEL_WARNING = 2
    LOG_LEVEL_ERROR = 3


class eDirType(Enum):
    """
    Enumeration for different working directory types.
    """
    DIR_TYPE_NONE = 0
    DIR_TYPE_LOG = 1
    DIR_TYPE_CONFIG = 2


class eFileType(Enum):
    """
    Enumeration for predefined log/config file types.
    """
    FILE_LOG = 1
    FILE_SYSERR = 2
    FILE_CONFIG = 3


T = TypeVar("T")

working_directories: Dict[eDirType, str] = {
    eDirType.DIR_TYPE_LOG: "log",
    eDirType.DIR_TYPE_CONFIG: "config"
}
"""Maps directory types to relative folder names."""


file_name_map: Dict[eFileType, str] = {
    eFileType.FILE_LOG: "log.txt",
    eFileType.FILE_SYSERR: "sysser.txt",
    eFileType.FILE_CONFIG: "config.cfg",
}
"""Maps file types to filenames."""


class CheckException(Exception):
    """
    Custom exception raised when a runtime check fails.
    """
    def __init__(self, err_message: str):
        super().__init__(f'Runtime error: {err_message}')


def singleton(class_: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that ensures only one instance of the class exists (singleton pattern).

    Args:
        class_ (Callable[..., T]): The class to decorate.

    Returns:
        Callable[..., T]: A function that always returns the same class instance.
    """
    instances: Dict[Callable[..., T], T] = {}

    @wraps(class_)
    def get_class_instance(*args, **kwargs) -> T:
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_class_instance

def require_valid_enum(enum_cls: Enum) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that ensures the first argument passed to a method is a valid value of the given Enum.

    Args:
        enum_cls (Enum): The enum class to validate against.

    Returns:
        Callable: Decorated function that validates enum range.

    Raises:
        ValueError: If the passed value is not a valid enum member.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self: Any, value: int, *args, **kwargs) -> T:
            if not any(value == item.value for item in enum_cls):
                raise ValueError(f"Invalid value {value} for enum {enum_cls.__name__}")
            return func(self, value, *args, **kwargs)
        return wrapper
    return decorator

def require_conditions(
    check_class_attr: str = None,
    check_args_not_null: bool = False,
    exception: Exception = CheckException
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that validates runtime conditions before executing a method.

    Args:
        check_class_attr (str, optional): Name of a class attribute that must be non-empty.
        check_args_not_null (bool, optional): Whether to check for None in args.
        exception (Exception): Exception class to raise on failure.

    Returns:
        Callable: Wrapped function with runtime checks.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self: Any, *args, **kwargs) -> T:
            if check_class_attr:
                value = getattr(self.__class__, check_class_attr, None)
                if not value:
                    raise exception(f"Class attribute '{check_class_attr}' is not set or empty.")

            if check_args_not_null:
                for arg in args:
                    if arg is None:
                        raise exception(f"Argument {arg} is null.")

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def format_enum(enum_value: Enum) -> str:
    """
    Formats an Enum member into a simple string representation like '<Log>'.

    Args:
        enum_value (Enum): Enum member.

    Returns:
        str: Formatted string.
    """
    name = enum_value.name
    return f"<{name.split('_')[-1].capitalize()}>"


def filename_from_enum(file_type: Enum) -> str:
    """
    Resolves a filename from a file-type Enum member.

    Args:
        file_type (Enum): Enum representing the type of file.

    Returns:
        str: File name corresponding to the enum value.
    """
    return file_name_map.get(file_type, "default.txt")
