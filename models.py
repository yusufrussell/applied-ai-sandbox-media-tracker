from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
import uuid


class MediaStatus(Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"
    ON_HOLD = "on_hold"


class MediaCategory(Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    BOOK = "book"
    ANIME = "anime"
    MANGA = "manga"
    GAME = "game"


@dataclass
class MediaItem:
    title: str
    status: MediaStatus = MediaStatus.PLANNING
    rating: Optional[int] = None  # 1–10; None means unrated
    notes: str = ""
    date_added: str = field(default_factory=lambda: date.today().isoformat())
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    @property
    def category(self) -> MediaCategory:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category.value,
            "status": self.status.value,
            "rating": self.rating,
            "notes": self.notes,
            "date_added": self.date_added,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MediaItem:
        """Factory — returns the correct subclass based on the category field."""
        subclass = _CATEGORY_MAP[data["category"]]
        return subclass(
            title=data["title"],
            status=MediaStatus(data["status"]),
            rating=data.get("rating"),
            notes=data.get("notes", ""),
            date_added=data.get("date_added", date.today().isoformat()),
            id=data["id"],
        )


class Movie(MediaItem):
    @property
    def category(self) -> MediaCategory:
        return MediaCategory.MOVIE


class TVShow(MediaItem):
    @property
    def category(self) -> MediaCategory:
        return MediaCategory.TV_SHOW


class Book(MediaItem):
    @property
    def category(self) -> MediaCategory:
        return MediaCategory.BOOK


class Anime(MediaItem):
    @property
    def category(self) -> MediaCategory:
        return MediaCategory.ANIME


class Manga(MediaItem):
    @property
    def category(self) -> MediaCategory:
        return MediaCategory.MANGA


class Game(MediaItem):
    @property
    def category(self) -> MediaCategory:
        return MediaCategory.GAME


# Populated after subclass definitions so from_dict can reference them.
_CATEGORY_MAP: dict[str, type[MediaItem]] = {
    MediaCategory.MOVIE.value: Movie,
    MediaCategory.TV_SHOW.value: TVShow,
    MediaCategory.BOOK.value: Book,
    MediaCategory.ANIME.value: Anime,
    MediaCategory.MANGA.value: Manga,
    MediaCategory.GAME.value: Game,
}


class MediaLibrary:
    def __init__(self, items: list[MediaItem] | None = None) -> None:
        self._items: list[MediaItem] = list(items) if items else []

    def add(self, item: MediaItem) -> None:
        self._items.append(item)

    def get(self, item_id: str) -> Optional[MediaItem]:
        return next((i for i in self._items if i.id == item_id), None)

    def remove(self, item_id: str) -> bool:
        before = len(self._items)
        self._items = [i for i in self._items if i.id != item_id]
        return len(self._items) < before

    def all(self) -> list[MediaItem]:
        return list(self._items)

    def filter_by_category(self, category: MediaCategory) -> list[MediaItem]:
        return [i for i in self._items if i.category == category]

    def filter_by_status(self, status: MediaStatus) -> list[MediaItem]:
        return [i for i in self._items if i.status == status]

    def search(self, query: str) -> list[MediaItem]:
        q = query.lower()
        return [i for i in self._items if q in i.title.lower()]

    def sort_by(self, key: str, descending: bool = False) -> list[MediaItem]:
        if key == "rating":
            # Unrated items always sort to the end regardless of direction.
            rated = sorted(
                (i for i in self._items if i.rating is not None),
                key=lambda i: i.rating,  # type: ignore[arg-type]
                reverse=descending,
            )
            unrated = [i for i in self._items if i.rating is None]
            return rated + unrated
        if key == "title":
            return sorted(self._items, key=lambda i: i.title.lower(), reverse=descending)
        if key == "date":
            return sorted(self._items, key=lambda i: i.date_added, reverse=descending)
        return list(self._items)

    def to_dict(self) -> list[dict]:
        return [i.to_dict() for i in self._items]

    @classmethod
    def from_dict(cls, data: list[dict]) -> MediaLibrary:
        return cls([MediaItem.from_dict(item) for item in data])
