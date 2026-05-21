from typing import Protocol


class Storage(Protocol):
    def write_bytes(self, relative_path: str, content: bytes) -> str:
        ...

    def read_bytes(self, relative_path: str) -> bytes:
        ...
