from abc import ABC, abstractmethod

class Entity(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @name.setter
    @abstractmethod
    def name(self, name:str):
        pass

    @abstractmethod
    def update(self):
        pass

    