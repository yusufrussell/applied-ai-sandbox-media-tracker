"""Tests for the OOP data model: MediaItem subclasses and MediaLibrary."""
import json
from pathlib import Path

import pytest

from models import (
    Anime,
    Book,
    Game,
    Game,
    Manga,
    MediaCategory,
    MediaItem,
    MediaLibrary,
    MediaStatus,
    Movie,
    TVShow,
)


# ── MediaItem / subclasses ─────────────────────────────────────────────────

def test_movie_has_correct_category():
    m = Movie("Dune")
    assert m.category == MediaCategory.MOVIE


def test_subclass_defaults():
    b = Book("Dune Messiah")
    assert b.status == MediaStatus.PLANNING
    assert b.rating is None
    assert b.notes == ""
    assert b.id  # auto-generated, non-empty


def test_from_dict_returns_correct_subclass():
    data = {
        "title": "Frieren",
        "category": "anime",
        "status": "completed",
        "rating": 10,
        "notes": "",
        "date_added": "2026-01-01",
        "id": "abc123",
    }
    item = MediaItem.from_dict(data)
    assert isinstance(item, Anime)
    assert item.title == "Frieren"
    assert item.rating == 10
    assert item.id == "abc123"


def test_from_dict_auto_generates_id_when_absent():
    item = MediaItem.from_dict({
        "title": "Test", "category": "game",
        "status": "planning",
    })
    assert item.id  # should be non-empty string


def test_to_dict_round_trip():
    original = TVShow("Breaking Bad", status=MediaStatus.COMPLETED, rating=9)
    restored = MediaItem.from_dict(original.to_dict())
    assert type(restored) is TVShow
    assert restored.title == original.title
    assert restored.status == original.status
    assert restored.rating == original.rating
    assert restored.id == original.id


# ── MediaLibrary ───────────────────────────────────────────────────────────

def test_library_add_and_all():
    lib = MediaLibrary()
    lib.add(Movie("Dune"))
    lib.add(Book("Dune Messiah"))
    assert len(lib.all()) == 2


def test_library_get_returns_item():
    lib = MediaLibrary()
    m = Movie("Dune")
    lib.add(m)
    assert lib.get(m.id) is m


def test_library_get_returns_none_for_unknown_id():
    assert MediaLibrary().get("no-such-id") is None


def test_library_remove_returns_true_and_removes():
    lib = MediaLibrary()
    m = Movie("Dune")
    lib.add(m)
    result = lib.remove(m.id)
    assert result is True
    assert lib.get(m.id) is None


def test_library_remove_returns_false_for_unknown_id():
    assert MediaLibrary().remove("no-such-id") is False


def test_library_filter_by_category():
    lib = MediaLibrary()
    lib.add(Movie("Dune"))
    lib.add(Movie("Inception"))
    lib.add(Book("Dune Messiah"))
    movies = lib.filter_by_category(MediaCategory.MOVIE)
    assert len(movies) == 2
    assert all(isinstance(i, Movie) for i in movies)


def test_library_filter_by_status():
    lib = MediaLibrary()
    lib.add(Movie("Dune", status=MediaStatus.COMPLETED))
    lib.add(Movie("Inception", status=MediaStatus.PLANNING))
    completed = lib.filter_by_status(MediaStatus.COMPLETED)
    assert len(completed) == 1
    assert completed[0].title == "Dune"


def test_library_search_case_insensitive():
    lib = MediaLibrary()
    lib.add(Movie("Dune"))
    lib.add(Movie("Dune Messiah"))
    lib.add(Anime("Frieren"))
    results = lib.search("dune")
    assert len(results) == 2
    assert all("Dune" in i.title for i in results)


def test_library_search_no_match_returns_empty():
    lib = MediaLibrary()
    lib.add(Movie("Dune"))
    assert lib.search("zzznomatch") == []


def test_library_sort_by_rating_descending():
    lib = MediaLibrary()
    lib.add(Movie("A", rating=7))
    lib.add(Movie("B", rating=10))
    lib.add(Movie("C", rating=None))  # unrated → last
    lib.add(Movie("D", rating=4))
    result = lib.sort_by("rating", descending=True)
    ratings = [i.rating for i in result]
    assert ratings == [10, 7, 4, None]


def test_library_sort_by_title():
    lib = MediaLibrary()
    lib.add(Movie("Zebra"))
    lib.add(Movie("Apple"))
    lib.add(Movie("Mango"))
    result = lib.sort_by("title")
    assert [i.title for i in result] == ["Apple", "Mango", "Zebra"]


def test_library_json_round_trip(tmp_path):
    lib = MediaLibrary()
    lib.add(Movie("Dune", status=MediaStatus.COMPLETED, rating=9))
    lib.add(Anime("Frieren", rating=10))
    data = lib.to_dict()
    restored = MediaLibrary.from_dict(data)
    assert len(restored.all()) == 2
    types = {type(i).__name__ for i in restored.all()}
    assert types == {"Movie", "Anime"}
