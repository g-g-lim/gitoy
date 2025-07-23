import hashlib
from typing import Protocol
from custom_types import ReadableBuffer


class HashAlgo(Protocol): 

    def hash(self, buffer: ReadableBuffer) -> None:
        ...


class Sha1(HashAlgo):

    def __init__(self):
        self._hash = hashlib.sha1()

    @classmethod
    def init(cls) -> HashAlgo:
        return cls()

    def hash(self, buffer: ReadableBuffer) -> None:
        self._hash.update(buffer)

    def digest(self) -> str:
        return self._hash.hexdigest()


