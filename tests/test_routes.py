"""Acceptance tests for Flask routes."""
from models import Anime, Book, Movie, MediaStatus


# ── Home ──────────────────────────────────────────────────────────────────

def test_home_empty_state(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Nothing tracked yet" in r.data


def test_home_shows_items(client, app):
    app.library.add(Movie("Dune", rating=9))
    r = client.get("/")
    assert b"Dune" in r.data
    assert b"9/10" in r.data


def test_home_category_filter(client, app):
    app.library.add(Movie("Dune"))
    app.library.add(Book("Dune Messiah"))
    r = client.get("/?category=book")
    assert b"Dune Messiah" in r.data
    assert b"Dune Messiah" in r.data
    # Movie should not appear in book-only view
    body = r.data.decode()
    assert "Movie" not in body.split("Dune Messiah")[0].split("Book")[-1]


def test_home_status_filter(client, app):
    app.library.add(Movie("Dune", status=MediaStatus.COMPLETED))
    app.library.add(Movie("Inception", status=MediaStatus.PLANNING))
    r = client.get("/?status=completed")
    assert b"Dune" in r.data
    assert b"Inception" not in r.data


def test_home_search(client, app):
    app.library.add(Movie("Dune"))
    app.library.add(Movie("Dune Messiah"))
    app.library.add(Anime("Frieren"))
    r = client.get("/?q=dune")
    assert b"Dune" in r.data
    assert b"Dune Messiah" in r.data
    assert b"Frieren" not in r.data


def test_home_search_no_results(client, app):
    app.library.add(Movie("Dune"))
    r = client.get("/?q=zzznomatch")
    assert b"No items match" in r.data


def test_home_sort_rating(client, app):
    app.library.add(Movie("Low", rating=3))
    app.library.add(Movie("High", rating=9))
    r = client.get("/?sort=rating")
    body = r.data.decode()
    assert body.index("High") < body.index("Low")


# ── Add ───────────────────────────────────────────────────────────────────

def test_add_get_renders_form(client):
    r = client.get("/add")
    assert r.status_code == 200
    assert b"Save" in r.data


def test_add_route_creates_item(client, app):
    r = client.post("/add", data={
        "title": "Dune", "category": "movie",
        "status": "completed", "rating": "9", "notes": "Great",
    })
    assert r.status_code in (302, 303)
    assert len(app.library.all()) == 1
    item = app.library.all()[0]
    assert item.title == "Dune"
    assert item.rating == 9


def test_add_requires_title(client, app):
    r = client.post("/add", data={
        "title": "", "category": "movie", "status": "planning",
    })
    assert r.status_code == 200
    assert b"Title is required" in r.data
    assert len(app.library.all()) == 0


def test_add_validates_rating_range(client):
    r = client.post("/add", data={
        "title": "Test", "category": "movie",
        "status": "planning", "rating": "11",
    })
    assert b"Rating must be between" in r.data


def test_add_accepts_no_rating(client, app):
    r = client.post("/add", data={
        "title": "No Rating", "category": "book", "status": "planning",
    })
    assert r.status_code in (302, 303)
    assert app.library.all()[0].rating is None


# ── Detail + Edit ─────────────────────────────────────────────────────────

def test_detail_renders(client, app):
    app.library.add(Movie("Dune", rating=9))
    item_id = app.library.all()[0].id
    r = client.get(f"/media/{item_id}")
    assert r.status_code == 200
    assert b"Dune" in r.data
    assert b"Save changes" in r.data


def test_detail_unknown_id_returns_404(client):
    assert client.get("/media/doesnotexist").status_code == 404


def test_edit_updates_item(client, app):
    app.library.add(Movie("Dune", rating=7))
    item_id = app.library.all()[0].id
    r = client.post(f"/media/{item_id}/edit", data={
        "status": "completed", "rating": "10", "notes": "Updated",
    })
    assert r.status_code in (302, 303)
    item = app.library.get(item_id)
    assert item.rating == 10
    assert item.notes == "Updated"


def test_edit_invalid_rating_does_not_save(client, app):
    app.library.add(Movie("Dune", rating=7))
    item_id = app.library.all()[0].id
    client.post(f"/media/{item_id}/edit", data={
        "status": "completed", "rating": "99",
    })
    assert app.library.get(item_id).rating == 7


# ── Delete ────────────────────────────────────────────────────────────────

def test_delete_route_removes_item(client, app):
    app.library.add(Movie("Dune"))
    app.library.add(Book("Dune Messiah"))
    item_id = app.library.all()[0].id
    r = client.post(f"/media/{item_id}/delete")
    assert r.status_code in (302, 303)
    assert len(app.library.all()) == 1


def test_delete_nonexistent_returns_404(client):
    assert client.post("/media/doesnotexist/delete").status_code == 404


def test_delete_get_returns_405(client, app):
    app.library.add(Movie("Dune"))
    item_id = app.library.all()[0].id
    assert client.get(f"/media/{item_id}/delete").status_code == 405
