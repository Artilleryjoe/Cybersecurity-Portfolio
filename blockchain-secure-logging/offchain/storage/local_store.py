"""Append-only local storage facade for manifests and log batches."""

from __future__ import annotations

import json
import os
import pathlib
from datetime import datetime
from typing import Any, Dict


class AppendOnlyStore:
    """A simple write-once store that appends JSON records to disk."""

    def __init__(self, root: pathlib.Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> pathlib.Path:
        return self.root / name

    def append_json(self, name: str, payload: Dict[str, Any]) -> pathlib.Path:
        """Append a JSON record to ``name`` with a timestamp suffix."""

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        path = self._path_for(f"{name}.{timestamp}.json")
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing {path}")
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        os.chmod(path, 0o440)
        return path


__all__ = ["AppendOnlyStore"]
