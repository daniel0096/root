from abstract import Entity

class Entity(Entity):
    def __init__(self):
        self.entity_name = None

    @property
    def name(self) -> str:
        self.entity_name

    @name.setter
    def name(self, name:str):
        self.entity_name = name

    def update(self):
        pass
