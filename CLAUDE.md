# CLAUDE.md

## What this project is

A personal media list tracker — one Flask app that replaces scattered
third-party sites (Letterboxd, MAL, Goodreads, etc.). Tracks movies,
TV shows, books, anime, manga, and games in one place. Each entry has
a title, category, status, a 1–10 rating, and optional notes.

## Stack

- Python 3.10+, Flask 3.x, Jinja2 templates
- Plain JSON file (`data.json`) for persistence — no database
- pytest for tests
- OOP core in `models.py`: `MediaItem` base class, one subclass per
  media type, and a `MediaLibrary` manager class

## How to run

```bash
# Install dependencies
pip install flask pytest

# Run the app
python app.py
# → http://localhost:5000

# Run tests
pytest -q
```

## Project structure

```
media-tracker/
├── app.py          # create_app() factory; all routes defined inside
├── models.py       # MediaItem, subclasses, MediaLibrary
├── storage.py      # load/save MediaLibrary to data.json
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── add.html
│   └── detail.html
├── static/
│   └── style.css
├── tests/
│   ├── conftest.py
│   └── test_models.py
├── data.json       # runtime data — do not commit (gitignored)
└── CLAUDE.md
```

## Conventions

- Type hints on all function signatures
- `create_app()` factory pattern — attach library to `app.library`
- Small, focused functions (aim for under 25 lines per function)
- `snake_case` for Python identifiers; `kebab-case` for URL routes
- Routes follow the pattern: `GET` to render, `POST` to mutate, redirect after POST
- Enums for `MediaStatus` and `MediaCategory` — never use raw strings for these values
- `MediaItem.from_dict(data)` is the single factory for deserializing any media type

## Do not

- Add new `pip` packages without asking first
- Modify tests to make them pass — the tests are the spec
- Use a database (SQLite, SQLAlchemy, or anything else)
- Add user authentication or sessions
- Refactor code outside the current task's scope
- Use global state — all state lives on the `app` instance or is passed explicitly
