# BUILD_LOG.md — Media Tracker

## Task 1 — Scaffold repo + CLAUDE.md
- **Brief:** Create the GitHub repo, clone it, author CLAUDE.md covering project purpose, stack, conventions, and hard constraints for Claude Code sessions.
- **What Claude proposed:** A CLAUDE.md with six sections: what the project is, stack, how to run, project structure, conventions, and do-not list. Conventions included type hints, `create_app()` factory pattern, snake_case, and small focused functions.
- **What I changed before approving:** Nothing — the structure matched the plan exactly.
- **Verification:** Repo visible on GitHub with CLAUDE.md committed on main.
- **One thing I learned:** Writing the "Do not" section first forces you to think about what you actually care about. "Don't use a database" and "don't add auth" saved me from Claude suggesting both in later tasks.

---

## Task 2 — OOP data model
- **Brief:** Write `models.py` with `MediaStatus`/`MediaCategory` enums, `MediaItem` dataclass, six subclasses (Movie, TVShow, Book, Anime, Manga, Game), and `MediaLibrary` manager with add/get/remove/filter/search/sort.
- **What Claude proposed:** Exactly the above, plus `to_dict()`/`from_dict()` for JSON round-trip on both `MediaItem` and `MediaLibrary`. `_CATEGORY_MAP` dict for subclass dispatch in `from_dict`.
- **What I changed before approving:** Nothing structural, but verified the `sort_by("rating")` behavior: unrated items always go to the end regardless of sort direction — that's the right call.
- **Verification:** `python -c "from models import Movie, MediaLibrary; lib = MediaLibrary(); lib.add(Movie('Dune')); print(lib.all())"` printed the item. Filter, sort, search, and round-trip all verified in a one-liner script.
- **One thing I learned:** Defining `_CATEGORY_MAP` after all subclass definitions (not before) is required because the subclasses need to exist before they can be referenced as values in the dict. Order matters in Python module-level code.

---

## Task 3 — JSON persistence
- **Brief:** Write `storage.py` with `save(library, path)` and `load(path)` functions. `load()` should return an empty library when the file doesn't exist yet.
- **What Claude proposed:** A 21-line module — `save()` calls `json.dumps(library.to_dict())` and writes with `pathlib`; `load()` checks `path.exists()` before reading.
- **What I changed before approving:** Nothing — the serialization logic already lived in `MediaLibrary.to_dict()` and `MediaItem.from_dict()` from Task 2, so `storage.py` was correctly kept as a thin I/O wrapper.
- **Verification:** Created items, saved to a temp file, deleted the in-memory library, reloaded from disk, confirmed all 3 items and their correct subclass types (`Movie`, `Book`, `Anime`) survived the round-trip. Also confirmed loading a missing file returns an empty library.
- **One thing I learned:** Keeping serialization logic in the model (`to_dict`/`from_dict`) and I/O logic in storage is the right separation. If I'd put both in `storage.py`, tests would have needed to import storage just to test model behavior.

---

## Task 4 — Flask app shell + home route
- **Brief:** `app.py` with `create_app()` factory. Home route loads library, groups items by category, renders `home.html`. Write `templates/base.html` (nav) and `templates/home.html`.
- **What Claude proposed:** `create_app()` with a context processor injecting `categories` into all templates, home route building a `grouped` dict keyed by `MediaCategory`, and a `base.html` with category nav links.
- **What I changed before approving:** Claude flagged that the template referenced `url_for('add')` and `url_for('detail')` before those routes existed — the app would 500 immediately. Stub routes were added for both so templates stayed renderable at every task boundary.
- **Verification:** Flask test client confirmed: 200 on `/`, empty-state message present, `+ Add` link present, category nav links for Movie and Anime present.
- **One thing I learned:** Templates fail at render time, not import time. A missing `url_for` target crashes the page even if no items would ever hit that code path — you can't defer it with an `{% if %}` block.

---

## Task 5 — Add media entry
- **Brief:** `GET /add` renders a form (title, category, status, rating, notes). `POST /add` validates, creates the right subclass, saves to disk, redirects home. Preserve form values on validation failure.
- **What Claude proposed:** Full form with validation: title required, rating must be 1–10 integer if provided. `MediaItem.from_dict()` used as the factory.
- **What I changed before approving:** `from_dict()` required an explicit `id` key — correct for loading saved data but wrong for new items where the dataclass `default_factory` should generate a fresh one. Updated `from_dict` to make `id` optional so new items get auto-generated IDs.
- **Verification:** All 12 assertions passed: GET renders form, empty title shows error, rating=11 shows error, valid POST redirects, item saved with correct title/type/status/rating/notes.
- **One thing I learned:** A factory method designed for deserialization (loading from disk) isn't automatically the right factory for construction (creating from user input). The two have different contracts around which fields are required.

---

## Task 6 — Category + status filter
- **Brief:** Home route reads `?category=` and `?status=` query params. Nav links highlight the active category and show per-category counts. Status filter bar with pill links. Both filters compose.
- **What Claude proposed:** Query param validation via `MediaCategory(value)` / `MediaStatus(value)` in try/except blocks (unknown values silently ignored). Count badges via the context processor. A "✕ Clear filters" link when any filter is active.
- **What I changed before approving:** Nothing structural. Verified that combined filters (`?category=movie&status=completed`) work correctly and that passing an invalid category string doesn't crash the app.
- **Verification:** 11 assertions: category filter shows/hides correct items, status filter works across categories, combined filter works, empty-filter message correct, count badges present, clear link present.
- **One thing I learned:** Silently ignoring invalid enum values (`except ValueError: pass`) is the right call for query params — returning a 400 would break links if a category is ever renamed. Graceful degradation beats strict validation at the URL layer.

---

## Task 7 — Detail + edit view
- **Brief:** `GET /media/<id>` renders a detail page. `POST /media/<id>/edit` updates status, rating, notes in place, saves, redirects back. Pre-populate form with current values.
- **What Claude proposed:** Two-column layout: info panel (all fields read-only) + edit form. Separate `edit` route for the POST. Validation mirrors the add route. Missing id → 404.
- **What I changed before approving:** The GET route passed `errors={}` but not `form={}` — the template used `form.get(...)` for pre-population and crashed with `UndefinedError` on every GET. Fixed by passing `form={}` alongside `errors={}`.
- **Verification:** GET renders title and "Not rated" for unrated item. Valid POST updates rating/status/notes. Invalid rating shows error without corrupting the item. Missing id returns 404. (A false failure on the "Not rated" check traced back to `data.json` from previous test runs being loaded — not a code bug.)
- **One thing I learned:** Always pass every variable the template references, even if it's just an empty dict. Jinja2's `UndefinedError` only fires at render time, not when writing the route, so missing template variables are easy to miss in code review.

---

## Task 8 — Delete
- **Brief:** `POST /media/<id>/delete` removes item, saves, redirects home. GET → 405. Unknown id → 404.
- **What Claude proposed:** Five-line route using `MediaLibrary.remove()` which returns `False` for unknown ids. Delete button on the detail page inside a `<form>` with a JS `confirm()` dialog.
- **What I changed before approving:** Nothing — the route correctly delegates "not found" detection to `remove()` returning `False` rather than calling `get()` first and then `remove()`.
- **Verification:** DELETE redirects (302), removes correct item, remaining item is correct. GET returns 405 (free from Flask's method registration). Missing id returns 404. Persisted correctly to temp JSON file. Delete button visible on detail page.
- **One thing I learned:** Using the return value of `remove()` to detect "not found" is cleaner than a separate `get()` check — it avoids a race condition (unlikely here, but good habit) and is fewer lines.

---

## Task 9 — Sort + search
- **Brief:** Home route reads `?sort=` (rating/title/date) and `?q=` (title search). All four params compose. Toolbar with search form and sort links.
- **What Claude proposed:** A `_sort()` helper above `create_app()` that handles rated/unrated split for rating sort. Filter → search → sort → group pipeline in the route. Hidden inputs in the search form to preserve active category/status filters on submit.
- **What I changed before approving:** Nothing structural. A verification test initially failed because `'Dune"'` didn't match the template output — but that was a test-string issue, not a code bug. The real check (position comparison) passed correctly.
- **Verification:** Sort by rating puts Dune(9) before Inception(7) before unrated within the Movie section. Sort by title is A–Z. Search `?q=du` returns Dune and Dune Messiah, hides Frieren and Inception. Combined `?q=du&category=book` returns only Dune Messiah. Empty state fires for search with no results.
- **One thing I learned:** Sort within category groups (not globally) is the right design for a grouped layout — globally sorting would break the visual category structure and is confusing when items from different categories are interleaved.

---

## Task 10 — Tests + README
- **Brief:** `tests/conftest.py` with app + client fixtures. At least 4 tests covering model logic and routes. `README.md`.
- **What Claude proposed:** 36 tests split across `test_models.py` (unit tests: filter, search, sort, round-trip, subclass factory) and `test_routes.py` (acceptance tests: add/edit/delete/home filters/search/sort). `conftest.py` replaces `app.library` with a fresh `MediaLibrary()` per test.
- **What I changed before approving:** Nothing — the test isolation strategy (replacing `app.library` in the fixture) was the right call and correctly identified upfront.
- **Verification:** `pytest -q` → 36 passed, 0 failed, 0.25s.
- **One thing I learned:** Test isolation is the most important decision in `conftest.py`. `create_app()` loads `data.json` on startup, so without replacing `app.library`, every test would inherit leftover data from manual testing sessions and tests would fail non-deterministically.
