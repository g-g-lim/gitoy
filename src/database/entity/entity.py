from dataclasses import dataclass

@dataclass
class Entity:   

    @staticmethod
    def columns():
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod 
    def table_name():
        raise NotImplementedError("Subclasses must implement this method")