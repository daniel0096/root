import log
from entity import Entity

class Character(Entity):
    def __init__(self, name: str):
        self._name = name

    