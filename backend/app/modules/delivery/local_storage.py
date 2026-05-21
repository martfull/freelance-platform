from pathlib import Path

from app.core.config import get_settings


class LocalStorage:
    def __init__(self, root_path: str | None = None) -> None:
        settings = get_settings()
        self.root_path = Path(root_path or settings.storage_path)

    def write_bytes(self, relative_path: str, content: bytes) -> str:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return relative_path

    def read_bytes(self, relative_path: str) -> bytes:
        return self._resolve(relative_path).read_bytes()

    def _resolve(self, relative_path: str) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError("Storage path must be relative")
        return self.root_path.joinpath(candidate)
