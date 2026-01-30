from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    term_idx: int = 0
    photo_idx: int = 0
    current_api: str = 'pexels'
    photos_cache: dict[int, list[Any]] = field(default_factory=dict)

    def reset_photo_idx(self):
        self.photo_idx = 0

    def clear_cache(self):
        self.photos_cache = {}

# Global instance for single-user app
session = SessionState()
