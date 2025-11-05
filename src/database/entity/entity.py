from dataclasses import dataclass


@dataclass
class Entity:
    @property
    def primary_key(self):
        return getattr(self, self.primary_key_column())

    @staticmethod
    def columns():
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def primary_key_column():
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def table_name():
        raise NotImplementedError("Subclasses must implement this method")
