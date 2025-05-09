from file_manager import FileManager
from menu import Menu

from typing import Optional
from log import TRACE_LOG

class Game:
    def __init__(self):
        self._state: int = 0

        self.menu_instance = Menu()
        self.manager_instance = FileManager()
    
    def __repr__(self) -> str:
        return "Game(self):"

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, new_state: int):
        self._state = new_state

    def run(self):
        self.menu_instance.build_menu()
