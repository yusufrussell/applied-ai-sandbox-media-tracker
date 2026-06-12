from __future__ import annotations

import json
from pathlib import Path

from models import MediaLibrary

DEFAULT_PATH = Path("data.json")


def save(library: MediaLibrary, path: Path | str = DEFAULT_PATH) -> None:
    path = Path(path)
    path.write_text(json.dumps(library.to_dict(), indent=2), encoding="utf-8")


def load(path: Path | str = DEFAULT_PATH) -> MediaLibrary:
    path = Path(path)
    if not path.exists():
        return MediaLibrary()
    data = json.loads(path.read_text(encoding="utf-8"))
    return MediaLibrary.from_dict(data)
