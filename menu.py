from log import Log
from utils import require_valid_enum, eMenuState, eLogLevel, DEBUG_MODE

class Menu:
    def __init__(self):
        self._menu_state = eMenuState.MENU_STATE_NONE.value
        self.log_instance = Log()

    @property
    def menu_state(self) -> int:
        return self._menu_state

    @menu_state.setter
    @require_valid_enum(eMenuState)
    def menu_state(self, new_state: int):
        if DEBUG_MODE:
            self.log_instance.TRACE_LOG = (eLogLevel.LOG_LEVEL_LOG, f"Setting new menu state: {new_state}")
        self._menu_state = new_state
