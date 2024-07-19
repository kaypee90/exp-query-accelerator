from abc import ABC, abstractmethod

class BaseDatabaseWrapper(ABC):
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    @abstractmethod
    def query(self, **kwargs):
        pass