import pygame
from file_manager import FileManager
from utils import eDirType as eDir
from typing import Optional

class Game:
    def __init__(self):
        self._state: int = 0
        self.manager_instance = FileManager()

        self.manager_instance.build_init_files()

    def __repr__(self) -> str:
        return "Game(self):"

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, new_state: int):
        self._state = new_state

    def run(self):
        """
        test implementation!!!
        """
        pygame.init()
        background_colour = (100, 240, 255)
        (width, height) = (1080, 768)
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Game')
        screen.fill(background_colour)
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()
